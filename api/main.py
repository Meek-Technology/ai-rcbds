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
    design_shear_reinforcement
)
from api.report import generate_pdf

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
        )

        w = loads_data["w_total_udl"]
        p1 = loads_data["p1_point_load"]

        # Build per-span loading list
        span_loads = []
        for s in spans_list:
            if load_type == "point_load" and p1 > 0:
                span_loads.append({"type": "point_load", "P": p1, "a": s / 2})
            else:
                span_loads.append({"type": "udl", "w": w})

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
            )
            w = loads_data["w_total_udl"]
            p1 = loads_data["p1_point_load"]

            # Rebuild span loads and re-solve with updated UDL
            span_loads = []
            for s in spans_list:
                if load_type == "point_load" and p1 > 0:
                    span_loads.append({"type": "point_load", "P": p1, "a": s / 2})
                else:
                    span_loads.append({"type": "udl", "w": w})
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
                "w_total_udl": loads_data["w_total_udl"],
                "p1_point_load": loads_data["p1_point_load"],
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
    beam_size = estimate_beam_size(span, beam_type)

    # ── Step 2: Calculate factored loads (BS 8110) ──
    # n1 = slab/user load (UDL), n2 = beam self-weight, n3 = wall load, p1 = point load
    slab_load = params.get("slab_load", 0) or load  # Use slab_load if given, else user's 'load'

    # For overhang + point load only (no UDL from user), set slab_load = 0
    if beam_type == "overhang" and load_type == "point_load" and not params.get("slab_load"):
        slab_load = 0
        point_load = load  # The user's load IS the point load

    loads = design_loads(
        slab_load=slab_load,
        beam_width_mm=beam_size["width"],
        beam_depth_mm=beam_size["depth"],
        wall_density=params.get("density", 0),
        wall_thickness=params.get("wall_thickness", 0),
        wall_height=params.get("wall_height", 0),
        point_load=point_load,
    )

    w = loads["w_total_udl"]       # Total UDL = n1 + n2 + n3
    p1 = loads["p1_point_load"]    # Point load (separate)

    # ── Step 3: Calculate design moment (M_udl + M_point) ──
    moments = design_moment(w, span, beam_type, p1, load_position, overhang_length)

    # ── Step 4: BS 8110 Bending Reinforcement Design ──
    M_total = moments["M_total"]
    reinf_result, final_w, final_d, resized = design_reinforcement_with_resize(
        M_total, beam_size["width"], beam_size["depth"], fck, fy
    )

    # If beam was resized, update beam_size
    if resized:
        beam_size = {"width": final_w, "depth": final_d}

    As_req = reinf_result["As_req"]
    best_reinf, options = recommend_reinforcement(As_req)

    # ── Step 5: BS 8110 Deflection check (Table 3.9) ──
    defl_result, As_prov_final, h_final, defl_reinf, defl_fixed = deflection_check_with_fix(
        span, beam_size["width"], beam_size["depth"],
        M_total, As_req, best_reinf["provided_area"],
        fy, fck, beam_type
    )

    # If deflection fix changed the beam depth or reinforcement, update
    if defl_fixed:
        if h_final != beam_size["depth"]:
            beam_size = {"width": beam_size["width"], "depth": h_final}
            resized = True
            # Recalculate reinforcement for new depth
            reinf_result = design_bending_reinforcement(M_total, beam_size["width"], h_final, fck, fy)
            As_req = reinf_result["As_req"]
        best_reinf = defl_reinf
        best_reinf, options = recommend_reinforcement(As_prov_final)

    deflection_status = defl_result["status"]

    # ── Step 6: Shear & diagrams ──
    shear = max_shear_force(w, span, beam_type, "udl", overhang_length=overhang_length)
    x, shear_curve, moment_curve, load_curve = generate_diagrams(
        w, span, beam_type, "udl", overhang_length=overhang_length
    )

    # If there's also a point load, generate combined diagrams
    if p1 > 0:
        shear_p = max_shear_force(p1, span, beam_type, "point_load", load_position, overhang_length)
        shear = shear + shear_p  # Combined max shear (conservative)

        # For overhang with point load and no UDL, use point load diagrams directly
        if beam_type == "overhang" and w <= loads["n2_beam_self_weight"] + 0.01:
            x, shear_curve, moment_curve, load_curve = generate_diagrams(
                p1, span, beam_type, "point_load", load_position, overhang_length
            )

    # ── Step 7: Shear reinforcement design ──
    shear_reinf = design_shear_reinforcement(
        shear, beam_size["width"], beam_size["depth"],
        best_reinf["provided_area"], fck
    )

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
            "M_udl": moments["M_udl"],
            "M_point": moments["M_point"],
            "max_shear_force": round(shear, 2),
            "n1_slab_load": loads["n1_slab_load"],
            "n2_beam_self_weight": loads["n2_beam_self_weight"],
            "n3_wall_load": loads["n3_wall_load"],
            "w_total_udl": loads["w_total_udl"],
            "p1_point_load": loads["p1_point_load"],
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

    # reuse prediction logic
    result = predict(data)

    # If predict returned a JSONResponse (error), forward it
    if isinstance(result, JSONResponse):
        return result

    file_path = generate_pdf(result)

    return FileResponse(file_path, filename="ai_beam_report.pdf", media_type='application/pdf')


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Structural Design System is running..."
    }


@app.get("/info")
def system_info():
    return {
        "project": "AI Structural Beam Design System",
        "developer": "MEEK Technology",
        "features": [
            "AI prediction",
            "Prompt-based input",
            "Graph visualization",
            "Wall load calculation",
            "Reinforcement design",
            "PDF report generation",
            "Multiple beam types (Simply Supported, Cantilever, Continuous, Overhang)",
            "Multiple load types (UDL, Point Load, Triangular)",
            "Support conditions (Roller, Pinned, Fixed)"
        ]
    }


@app.get("/version")
def version():
    return {
        "version": "2.1.0",
        "release": "Final Year Project",
        "year": 2026
    }


@app.get("/example")
def example_input():
    return {
        "examples": [
            {"prompt": "Design a simply supported beam with span 6m, UDL of 25kN/m, concrete grade 30 and steel grade 500"},
            {"prompt": "Design a cantilever beam with span 4m, point load of 30kN at 4m"},
            {"prompt": "Design a continuous beam with span 8m and UDL 20kN/m"},
            {"prompt": "Design a simply supported beam with span 5m and triangular load of 15kN/m"},
        ]
    }



app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
