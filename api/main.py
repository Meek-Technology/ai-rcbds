from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import joblib
import pandas as pd

from nlp.prompt_parser import extract_parameters, apply_defaults
from rules.beam_design import (
    bending_moment, recommend_reinforcement, estimate_beam_size,
    generate_diagrams, max_shear_force, design_loads, design_moment,
    design_bending_reinforcement, design_reinforcement_with_resize, effective_depth,
    check_deflection_bs8110, deflection_check_with_fix,
    design_shear_reinforcement, design_moment_multi, max_shear_force_multi,
    generate_diagrams_multi
)
from api.report import generate_pdf
from api.calc_sheet import generate_calc_sheet

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")


@app.post("/parse")
def parse_prompt(data: dict):
    """Parse a prompt and return extracted parameters for user confirmation."""
    try:
        if "prompt" not in data:
            return JSONResponse(status_code=400, content={"error": "No prompt provided."})

        params = extract_parameters(data["prompt"])
        params = apply_defaults(params)
        return {"parsed": params}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/predict")
def predict(data: dict):

    # Handle prompt input or direct parameters
    try:
        if "prompt" in data:
            params = extract_parameters(data["prompt"])
            params = apply_defaults(params)
        else:
            params = data
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    span = params["span"]
    load = params["load"]             # User-provided load (slab load / UDL)
    fck = params.get("fcu") or params.get("fck") or 25.0
    fy = params.get("fy") or 460.0

    beam_type = params.get("beam_type", "simply_supported")
    load_type = params.get("load_type", "udl")
    load_position = params.get("load_position")
    point_load = params.get("point_load", 0)
    overhang_length = params.get("overhang_length") or 0
    slab_load = 0

    # Extract multiple point loads list from parsed params
    point_loads_list = None
    if params.get("point_loads"):
        point_loads_list = params["point_loads"]
    elif params.get("loads"):
        point_loads_list = [ld for ld in params["loads"] if ld.get("type") == "point_load"]

    # ═══════════════════════════════════════════════
    #  CONTINUOUS BEAM → Three-Moment Solver
    # ═══════════════════════════════════════════════
    if beam_type == "continuous" and params.get("spans"):
        from rules.continuous_beam import solve_three_moment, merge_diagrams

        spans_list = params["spans"]
        supports_list = params.get("supports") or ["pinned"] * (len(spans_list) + 1)

        # Estimate beam size from the longest span
        max_span = max(spans_list)
        beam_size = estimate_beam_size(max_span, beam_type)

        # Calculate factored loads (BS 8110)
        slab_load = params.get("slab_load", 0) or load
        loads_data = design_loads(
            slab_load=slab_load,
            beam_width_mm=beam_size["width"],
            beam_depth_mm=beam_size["depth"],
            wall_density=params.get("density", 0),
            wall_thickness=params.get("wall_thickness", 0),
            wall_height=params.get("wall_height", 0),
            point_load=point_load,
            point_loads_list=point_loads_list,
        )

        w = loads_data["w_total_udl"]
        p1 = loads_data["p1_point_load"]

        # Build per-span loading list
        span_loads = _build_continuous_span_loads(
            params, spans_list, loads_data, load_type, w, p1
        )

        # Solve using Three-Moment Theorem
        result = solve_three_moment(spans_list, span_loads, supports_list)

        # Merge diagrams for plotting
        x, shear_curve, moment_curve, load_curve = merge_diagrams(result["diagrams"])

        # ══════════════════════════════════════════════
        #  BS 8110 Reinforcement Design — per location
        # ══════════════════════════════════════════════
        b_mm = beam_size["width"]
        h_mm = beam_size["depth"]
        resized = False

        # First check if beam section is adequate for the largest moment
        max_abs_moment = result["max_moment"]
        check_result = design_bending_reinforcement(max_abs_moment, b_mm, h_mm, fck, fy)
        if not check_result["adequate"]:
            # Resize beam to accommodate the largest moment
            check_result, b_mm, h_mm, resized = design_reinforcement_with_resize(
                max_abs_moment, b_mm, h_mm, fck, fy
            )
            beam_size = {"width": b_mm, "depth": h_mm}
            # Recalculate loads with new beam size
            loads_data = design_loads(
                slab_load=slab_load,
                beam_width_mm=b_mm,
                beam_depth_mm=h_mm,
                wall_density=params.get("density", 0),
                wall_thickness=params.get("wall_thickness", 0),
                wall_height=params.get("wall_height", 0),
                point_load=point_load,
                point_loads_list=point_loads_list,
            )
            w = loads_data["w_total_udl"]
            p1 = loads_data["p1_point_load"]

            # Rebuild span loads in multi-load format and re-solve
            span_loads = _build_continuous_span_loads(
                params, spans_list, loads_data, load_type, w, p1
            )
            result = solve_three_moment(spans_list, span_loads, supports_list)
            x, shear_curve, moment_curve, load_curve = merge_diagrams(result["diagrams"])

        # ── Design reinforcement at each support (hogging moments) ──
        support_designs = []
        for i, M_sup in enumerate(result["moments"]):
            label = chr(65 + i)  # A, B, C, D...
            if abs(M_sup) > 0.01:
                rd = design_bending_reinforcement(M_sup, b_mm, h_mm, fck, fy)
                best_r, opts = recommend_reinforcement(rd["As_req"])
                support_designs.append({
                    "location": f"Support {label}",
                    "type": "hogging",
                    "M": rd["M"],
                    "K": rd["K"],
                    "K_used": rd["K_used"],
                    "z": rd["z"],
                    "As_req": rd["As_req"],
                    "reinforcement": f"{best_r['bars']}Y{best_r['diameter']}",
                    "As_prov": best_r["provided_area"],
                })
            else:
                support_designs.append({
                    "location": f"Support {label}",
                    "type": "hogging",
                    "M": 0.0, "K": 0, "K_used": 0, "z": 0,
                    "As_req": 0, "reinforcement": "N/A", "As_prov": 0,
                })

        # ── Design reinforcement at each span (sagging moments) ──
        span_designs = []
        for i, diag in enumerate(result["diagrams"]):
            label_l = chr(65 + i)
            label_r = chr(65 + i + 1)
            span_name = f"Span {label_l}-{label_r}"

            # Max sagging moment = max positive moment in the span
            max_sag = max(diag["moment"])  # positive = sagging
            if max_sag < 0.01:
                max_sag = max(abs(v) for v in diag["moment"])

            rd = design_bending_reinforcement(max_sag, b_mm, h_mm, fck, fy)
            best_r, opts = recommend_reinforcement(rd["As_req"])
            span_designs.append({
                "location": span_name,
                "type": "sagging",
                "M": rd["M"],
                "K": rd["K"],
                "K_used": rd["K_used"],
                "z": rd["z"],
                "As_req": rd["As_req"],
                "reinforcement": f"{best_r['bars']}Y{best_r['diameter']}",
                "As_prov": best_r["provided_area"],
                "span_length": spans_list[i],
            })

        # ── Overall governing reinforcement (largest As) ──
        all_designs = support_designs + span_designs
        governing = max(all_designs, key=lambda d: d["As_req"])
        best_reinf, options = recommend_reinforcement(governing["As_req"])

        # ── Deflection check (use span with largest sagging moment) ──
        major_span_design = max(span_designs, key=lambda d: d["M"])

        # BS 8110 deflection: use major span moment, governing As
        defl_result = check_deflection_bs8110(
            major_span_design["span_length"], b_mm, beam_size["depth"],
            major_span_design["M"], major_span_design["As_req"],
            major_span_design["As_prov"], fy, beam_type
        )
        deflection_status = defl_result["status"]

        # ── Shear reinforcement design ──
        shear_reinf = design_shear_reinforcement(
            result["max_shear"], b_mm, beam_size["depth"],
            best_reinf["provided_area"], fck
        )

        return {
            "input": params,

            "beam": {
                "width": beam_size["width"],
                "depth": beam_size["depth"],
                "resized": resized,
            },

            "loading": loads_data,

            "continuous": {
                "spans": spans_list,
                "supports": supports_list,
                "support_moments": result["moments"],
                "reactions": result["reactions"],
                "n_spans": len(spans_list),
                "support_designs": support_designs,
                "span_designs": span_designs,
                "span_loads": span_loads,
            },

            "design": {
                "M": governing["M"],
                "Mu": check_result["Mu"],
                "adequate": check_result["adequate"],
                "d": check_result["d"],
                "K": governing["K"],
                "K_used": governing["K_used"],
                "z": governing["z"],
                "message": check_result["message"],
            },

            "results": {
                "steel_area": governing["As_req"],
                "bending_moment": result["max_moment"],
                "M_udl": result["max_moment"],
                "M_point": 0,
                "max_shear_force": result["max_shear"],
                "n1_slab_load": loads_data["n1_slab_load"],
                "n2_beam_self_weight": loads_data["n2_beam_self_weight"],
                "n3_wall_load": loads_data["n3_wall_load"],
                "wall_unit_weight": loads_data["wall_unit_weight"],
                "wall_thickness": loads_data["wall_thickness"],
                "wall_height": loads_data["wall_height"],
                "wall_line_load": loads_data["wall_line_load"],
                "w_total_udl": loads_data["w_total_udl"],
                "p1_point_load": loads_data["p1_point_load"],
                "all_point_loads": loads_data.get("all_point_loads", []),
            },

            "deflection": {
                "status": defl_result["status"],
                "basic_ratio": defl_result["basic_ratio"],
                "actual_ratio": defl_result["actual_ratio"],
                "allowable_ratio": defl_result["allowable_ratio"],
                "fs": defl_result["fs"],
                "MF": defl_result["MF"],
                "MF_uncapped": defl_result["MF_uncapped"],
                "d": defl_result["d"],
                "message": defl_result["message"],
                "fixed": False,
            },

            "shear_design": shear_reinf,

            "reinforcement": {
                "recommended": f"{best_reinf['bars']}Y{best_reinf['diameter']}",
                "provided_area": best_reinf["provided_area"],
                "required_area": governing["As_req"],
                "all_options": options
            },

            "graphs": {
                "x": x,
                "shear": shear_curve,
                "moment": moment_curve,
                "load": load_curve
            }
        }

    # ═══════════════════════════════════════════════
    #  SINGLE-SPAN BEAMS (existing logic)
    # ═══════════════════════════════════════════════

    # ── Step 1: Estimate beam size (needed for self-weight) ──
    original_size = estimate_beam_size(span, beam_type)
    beam_size = dict(original_size)

    slab_load = params.get("slab_load", 0) or load  # Use slab_load if given, else user's 'load'

    # For overhang + point load only (no UDL from user), set slab_load = 0
    if beam_type == "overhang" and load_type == "point_load" and not params.get("slab_load"):
        slab_load = 0
        point_load = load  # The user's load IS the point load

    # Build user loads array ONCE before the iteration loop
    user_loads = _build_user_loads(params, load_type, load, load_position, slab_load)

    # Initialize loop variables to resolve static analysis unbound warnings
    loads = {}
    dead_udl = 0.0
    moments = {}
    reinf_result = {}
    defl_result = {}
    defl_fixed = False

    # We iterate to converge on the stable beam size and its associated self-weight
    for iteration in range(3):
        # ── Step 2: Calculate factored loads (BS 8110) ──
        loads = design_loads(
            slab_load=slab_load,
            beam_width_mm=beam_size["width"],
            beam_depth_mm=beam_size["depth"],
            wall_density=params.get("density", 0),
            wall_thickness=params.get("wall_thickness", 0),
            wall_height=params.get("wall_height", 0),
            point_load=point_load,
            point_loads_list=point_loads_list,
        )

        w = loads["w_total_udl"]       # Total UDL = n1 + n2 + n3
        p1 = loads["p1_point_load"]    # Point load (separate)

        # ── Step 3: Calculate design moment via superposition ──
        dead_udl = float(loads["n2_beam_self_weight"] + loads["n3_wall_load"])
        moments = design_moment_multi(user_loads, span, beam_type, overhang_length, dead_udl)
        M_total = moments["M_total"]

        # ── Step 4: BS 8110 Bending Reinforcement Design ──
        reinf_result, final_w, final_d, resized_bending = design_reinforcement_with_resize(
            M_total, beam_size["width"], beam_size["depth"], fck, fy
        )

        # ── Step 5: BS 8110 Deflection check (Table 3.9) ──
        temp_best, _ = recommend_reinforcement(reinf_result["As_req"])
        defl_result, As_prov_final, h_final, defl_reinf, defl_fixed = deflection_check_with_fix(
            span, final_w, final_d,
            M_total, reinf_result["As_req"], temp_best["provided_area"],
            fy, fck, beam_type
        )

        new_width = final_w
        new_depth = h_final if defl_fixed else final_d

        if new_width == beam_size["width"] and new_depth == beam_size["depth"]:
            # Converged
            if defl_fixed:
                best_reinf = defl_reinf
                best_reinf, options = recommend_reinforcement(As_prov_final)
                if h_final != final_d:
                    reinf_result = design_bending_reinforcement(M_total, new_width, h_final, fck, fy)
                    As_req = reinf_result["As_req"]
                else:
                    As_req = reinf_result["As_req"]
            else:
                As_req = reinf_result["As_req"]
                best_reinf, options = recommend_reinforcement(As_req)
            break
        else:
            # Update size and run again to update self-weight and moments
            beam_size = {"width": new_width, "depth": new_depth}
    else:
        # Fallback if it didn't break early
        best_reinf, options = recommend_reinforcement(reinf_result["As_req"])
        As_req = reinf_result["As_req"]

    resized = (beam_size["width"] != original_size["width"] or beam_size["depth"] != original_size["depth"])
    deflection_status = defl_result["status"]

    # ── Step 6: Shear & diagrams ──
    shear = max_shear_force_multi(user_loads, span, beam_type, overhang_length, dead_udl)
    x, shear_curve, moment_curve, load_curve = generate_diagrams_multi(
        user_loads, span, beam_type, overhang_length, dead_udl
    )

    # ── Step 7: Shear reinforcement design ──
    shear_reinf = design_shear_reinforcement(
        shear, beam_size["width"], beam_size["depth"],
        best_reinf["provided_area"], fck
    )

    # ── Compute M_udl and M_point from contributions ──
    contribs = moments.get("contributions", [])
    M_udl = round(sum(c["M"] for c in contribs if "UDL" in c.get("desc", "") or "Self-weight" in c.get("desc", "")), 2)
    M_point = round(sum(c["M"] for c in contribs if "Point load" in c.get("desc", "")), 2)

    return {
        "input": params,

        "beam": {
            "width": beam_size["width"],
            "depth": beam_size["depth"],
            "resized": resized,
        },

        "loading": loads,
        "moments": moments,

        "design": {
            "M": reinf_result["M"],
            "Mu": reinf_result["Mu"],
            "adequate": reinf_result["adequate"],
            "d": reinf_result["d"],
            "K": reinf_result["K"],
            "K_used": reinf_result["K_used"],
            "z": reinf_result["z"],
            "message": reinf_result["message"],
        },

        "results": {
            "steel_area": reinf_result["As_req"],
            "bending_moment": moments["M_total"],
            "M_udl": M_udl,
            "M_point": M_point,
            "max_shear_force": round(shear, 2),
            "n1_slab_load": loads["n1_slab_load"],
            "n2_beam_self_weight": loads["n2_beam_self_weight"],
            "n3_wall_load": loads["n3_wall_load"],
            "wall_unit_weight": loads["wall_unit_weight"],
            "wall_thickness": loads["wall_thickness"],
            "wall_height": loads["wall_height"],
            "wall_line_load": loads["wall_line_load"],
            "w_total_udl": loads["w_total_udl"],
            "p1_point_load": loads["p1_point_load"],
            "all_point_loads": loads.get("all_point_loads", []),
        },

        "deflection": {
            "status": defl_result["status"],
            "basic_ratio": defl_result["basic_ratio"],
            "actual_ratio": defl_result["actual_ratio"],
            "allowable_ratio": defl_result["allowable_ratio"],
            "fs": defl_result["fs"],
            "MF": defl_result["MF"],
            "MF_uncapped": defl_result["MF_uncapped"],
            "d": defl_result["d"],
            "message": defl_result["message"],
            "fixed": defl_fixed,
        },

        "shear_design": shear_reinf,

        "reinforcement": {
            "recommended": f"{best_reinf['bars']}Y{best_reinf['diameter']}",
            "provided_area": best_reinf["provided_area"],
            "required_area": reinf_result["As_req"],
            "all_options": options
        },

        "graphs": {
            "x": x,
            "shear": shear_curve,
            "moment": moment_curve,
            "load": load_curve
        }
    }


# ═══════════════════════════════════════════════
#  Helper: Build user loads array from parsed params
# ═══════════════════════════════════════════════
def _build_user_loads(params, load_type, load_value, load_position, slab_load):
    """
    Build the user-load array for single-span beams.
    This is the list of loads the USER specified (UDLs and point loads),
    NOT including beam self-weight or wall load (those are added as dead_udl).
    """
    loads_arr = params.get("loads")
    if loads_arr:
        # Deep copy so we don't mutate the original
        return [dict(ld) for ld in loads_arr]

    # No multi-load from parser — build from legacy fields
    result = []
    if load_type == "point_load":
        result.append({"type": "point_load", "P": load_value, "a": load_position})
    elif load_type == "combined":
        # Has both — slab_load acts as UDL, point_load is separate
        if slab_load and slab_load > 0:
            result.append({"type": "udl", "w": slab_load})
        pl = params.get("point_load", 0)
        if pl > 0:
            result.append({"type": "point_load", "P": pl, "a": load_position})
    else:
        # Pure UDL — slab_load is the user UDL
        if slab_load and slab_load > 0:
            result.append({"type": "udl", "w": slab_load})
        else:
            result.append({"type": "udl", "w": load_value})

    return result


# ═══════════════════════════════════════════════
#  Helper: Build per-span loads for continuous beams
# ═══════════════════════════════════════════════
def _build_continuous_span_loads(params, spans_list, loads_data, load_type, w, p1):
    """
    Build per-span loading arrays for the Three-Moment solver.
    Each span gets a list of load dicts. Dead loads (n2 + n3) are
    automatically appended to every span.
    """
    dead_udl = loads_data["n2_beam_self_weight"] + loads_data["n3_wall_load"]

    # Calculate cumulative span boundaries
    cum_spans = []
    curr = 0.0
    for s_len in spans_list:
        cum_spans.append((curr, curr + s_len))
        curr += s_len

    # Try parsed per-span loads first
    per_span = params.get("per_span_loads")
    if per_span:
        span_loads = [[dict(ld) for ld in span] for span in per_span]

        # Check if any global UDL in params["loads"] with start/end needs mapping
        global_loads = params.get("loads") or []
        for g_ld in global_loads:
            if g_ld.get("type") == "udl" and "start" in g_ld and "end" in g_ld:
                g_start = float(g_ld["start"])
                g_end = float(g_ld["end"])
                g_w = float(g_ld["w"])
                for s_idx, (c_start, c_end) in enumerate(cum_spans):
                    if c_end > c_start and g_start >= c_start - 0.01 and g_end <= c_end + 0.01:
                        if not any(ld["type"] == "udl" and abs(ld["w"] - g_w) < 1e-4 for ld in span_loads[s_idx]):
                            span_loads[s_idx].append({"type": "udl", "w": g_w})

        for s_list in span_loads:
            if dead_udl > 0:
                s_list.append({"type": "udl", "w": dead_udl})
        return span_loads

    # Try generic loads array (applied to all spans)
    loads_arr = params.get("loads") or []
    span_loads = []

    for s in spans_list:
        span_load_list = []
        if loads_arr:
            for ld in loads_arr:
                entry = dict(ld)
                # Clamp point load position to within span
                if entry.get("type") == "point_load":
                    if entry.get("a") is None or entry["a"] > s:
                        entry["a"] = s / 2
                span_load_list.append(entry)
        else:
            # Fallback to single-load legacy
            if load_type == "point_load" and p1 > 0:
                span_load_list.append({"type": "point_load", "P": p1, "a": s / 2})
            else:
                span_load_list.append({"type": "udl", "w": w})

        if dead_udl > 0:
            span_load_list.append({"type": "udl", "w": dead_udl})

        span_loads.append(span_load_list)

    return span_loads


def check_deflection(span, depth, beam_type="simply_supported"):
    limits = {
        "simply_supported": 20,
        "cantilever": 7,
        "continuous": 26,
        "overhang": 20,
    }

    limit = limits.get(beam_type, 20)
    allowable = span * 1000 / limit

    if depth >= allowable:
        return "SAFE"
    else:
        return "NOT SAFE"


@app.post("/download-report")
def download_report(data: dict):
    """Generate a PDF results report from the full design data."""
    try:
        file_path = generate_pdf(data)
        return FileResponse(file_path, filename="ai-rcbds_design_report.pdf", media_type='application/pdf')
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF generation failed: {str(e)}"})


@app.post("/download-calculation-sheet")
def download_calculation_sheet(data: dict):
    """Generate a detailed BS 8110 calculation sheet PDF."""
    try:
        file_path = generate_calc_sheet(data)
        return FileResponse(file_path, filename="ai-rcbds_calc_sheet.pdf", media_type='application/pdf')
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Calculation sheet generation failed: {str(e)}"})


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI-RCBDS (AI Reinforced Concrete Beam Design System) is running..."
    }


@app.get("/info")
def system_info():
    return {
        "Project": "AI-RCBDS (AI Reinforced Concrete Beam Design System)",
        "Developed by": "Engr. Micheal Shokunbi (MEEK TECHNOLOGY)",
        "Version": "Final Year Project - Civil Engineering - FUOYE (v2.5.0)",
        "Features": [
            "AI Machine Learning Prediction (RandomForest + XGBoost Ensembles)",
            "Natural Language Multi-Load Prompt Parser",
            "Multi-Span Continuous Beam Analysis (Three-Moment Theorem)",
            "Heterogeneous & Multi-Load Combinations (UDL + Multiple Point Loads)",
            "Dynamic Diagram Rendering (SFD, BMD, Load Diagrams)",
            "BS 8110 Factored Load & Structural Reinforcement Calculations",
            "Automatic Beam Resizing for Shear & Deflection Safety Compliance",
            "Professional PDF Design Reports & Detailed BS 8110 Calculation Sheets",
            "Multiple Beam Types (Simply Supported, Cantilever, Continuous, Overhang)",
            "Multiple Support Configurations (Roller, Pinned, Fixed, Cantilever Free-End)"
        ]
    }


@app.get("/version")
def version():
    return {
        "version": "2.5.0",
        "release": "Final Year Project - Multi-Load AI-RCBDS",
        "year": 2026
    }


@app.get("/example")
def example_input():
    return {
        "examples": [
            {
                "category": "Simply Supported - Multi-Load",
                "prompt": "Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m"
            },
            {
                "category": "Simply Supported - Multiple Point Loads",
                "prompt": "Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m"
            },
            {
                "category": "Simply Supported - Partial UDL & Point Load",
                "prompt": "Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m"
            },
            {
                "category": "Overhang Beam - Multi-Load",
                "prompt": "Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end"
            },
            {
                "category": "Overhang Beam - Multiple Point Loads",
                "prompt": "Overhang beam 5m span, 1.5m overhang, point loads 20kN at 3m and 15kN at 6.5m"
            },
            {
                "category": "Continuous Beam - Heterogeneous Spans & Loads",
                "prompt": "3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m"
            },
            {
                "category": "Continuous Beam - 2 Span Mixed Loads",
                "prompt": "Continuous beam spans 4m and 5m, UDL 18kN/m on first span, point load 35kN at 2.5m on second span"
            },
            {
                "category": "Cantilever Beam - Combined Loads",
                "prompt": "Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m"
            },
            {
                "category": "Continuous Beam - Fixed & Roller Supports (2-Span)",
                "prompt": "Analyze the continuous beam ABC. Support A is fixed, while B and C are roller supports. Span AB is 3 m and span BC is 4 m. A UDL 2 kN/m from 0 to 3m, while a 10 kN point load acts at the midpoint of BC."
            },
            {
                "category": "Continuous Beam - Fixed Ends & Roller (3-Span)",
                "prompt": "Analyze the continuous beam ABCD. Support A and D are fixed, while B and C are roller supports. Span AB = 12 m, BC = 12 m, and CD = 4 m. A UDL 20 kN/m from 12m to 24m, while a 250 kN point load acts at the midpoint of span CD."
            },
            {
                "category": "Single UDL with Material Grades",
                "prompt": "Design a simply supported beam with span 6m, UDL of 25kN/m, fcu 30 and fy 500"
            }
        ]
    }



app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
