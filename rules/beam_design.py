# rules/beam_design.py

import math

# Unit weight of reinforced concrete (kN/m³)
CONCRETE_UNIT_WEIGHT = 24.0

# BS 8110 partial safety factors
DEAD_LOAD_FACTOR = 1.4    # γ_G for dead/permanent loads
LIVE_LOAD_FACTOR = 1.6    # γ_Q for live/imposed loads


# ──────────────────────────────────────────────
#  Factored Load Calculations (BS 8110)
# ──────────────────────────────────────────────

def calc_beam_self_weight(width_mm, depth_mm):
    """
    Calculate factored beam self-weight (kN/m).
    n2 = 1.4 × (width × depth × 24)
    width_mm, depth_mm: beam dimensions in mm
    Returns: factored self-weight in kN/m
    """
    width_m = width_mm / 1000
    depth_m = depth_mm / 1000
    unfactored = width_m * depth_m * CONCRETE_UNIT_WEIGHT
    return round(DEAD_LOAD_FACTOR * unfactored, 3)


def calc_wall_load(density, thickness, height):
    """
    Calculate wall line load and factored wall load (kN/m).

    Wall Line Load = density × thickness × height
    n3 = 1.4 × Wall Line Load

    A wall exists only if BOTH height > 0 AND thickness > 0.

    density: unit weight of wall material (kN/m³), default 20.0 for hollow block masonry
    thickness: wall thickness (m)
    height: wall height (m)

    Returns dict:
        wall_line_load: unfactored wall load (kN/m)
        n3: factored wall load (kN/m)
    """
    if height > 0 and thickness > 0:
        wall_line_load = density * thickness * height
        n3 = DEAD_LOAD_FACTOR * wall_line_load
    else:
        wall_line_load = 0.0
        n3 = 0.0

    return {
        "wall_line_load": round(wall_line_load, 3),
        "n3": round(n3, 3),
    }


def design_loads(slab_load=0, beam_width_mm=230, beam_depth_mm=300,
                 wall_density=0, wall_thickness=0, wall_height=0,
                 point_load=0, point_loads_list=None, ignore_self_weight=False):
    """
    Calculate all factored load components per BS 8110.

    n1 = slab_load (provided, already factored, kN/m)
    n2 = beam self-weight (1.4 × b × d × 24, kN/m) [or 0.0 if ignore_self_weight is True]
    n3 = factored wall line load (1.4 × unit_weight × thickness × height, kN/m)
    p1 = point_load (kN) — legacy single point load

    point_loads_list: optional list of dicts [{"P": kN, "a": m}, ...]
        for multiple point loads.

    w = n1 + n2 + n3  (total UDL, kN/m)

    Returns dict with n1, n2, n3, w, p1, all_point_loads, and wall detail breakdown
    """
    n1 = slab_load
    if ignore_self_weight:
        n2 = 0.0
    else:
        n2 = calc_beam_self_weight(beam_width_mm, beam_depth_mm)

    wall_result = calc_wall_load(wall_density, wall_thickness, wall_height)
    n3 = wall_result["n3"]
    wall_line_load = wall_result["wall_line_load"]

    w = n1 + n2 + n3  # total UDL

    # Build the all_point_loads list from point_loads_list or legacy single value
    all_point_loads = []
    if point_loads_list:
        for pl in point_loads_list:
            all_point_loads.append({
                "P": round(pl["P"], 3),
                "a": round(pl.get("a") or 0, 3),
            })
    elif point_load > 0:
        all_point_loads.append({"P": round(point_load, 3), "a": 0})

    return {
        "n1_slab_load": round(n1, 3),
        "n2_beam_self_weight": round(n2, 3),
        "n3_wall_load": round(n3, 3),
        "wall_unit_weight": round(wall_density, 2),
        "wall_thickness": round(wall_thickness, 3),
        "wall_height": round(wall_height, 2),
        "wall_line_load": round(wall_line_load, 3),
        "w_total_udl": round(w, 3),
        "p1_point_load": round(point_load, 3),
        "all_point_loads": all_point_loads,
    }


def design_moment(w, span, beam_type="simply_supported",
                  point_load=0, load_position=None, overhang_length=0):
    """
    Calculate total design moment combining UDL and point load contributions.
    M_total = M_udl(w) + M_point(p1)

    For statically indeterminate (continuous) beams, BS 8110 coefficients
    are used instead of wL²/8.
    """
    if load_position is None:
        load_position = span / 2

    # UDL moment
    M_udl = bending_moment(w, span, beam_type, "udl",
                           overhang_length=overhang_length)

    # Point load moment (if any)
    M_point = 0
    if point_load > 0:
        M_point = bending_moment(point_load, span, beam_type, "point_load",
                                 load_position, overhang_length)

    return {
        "M_udl": round(M_udl, 2),
        "M_point": round(M_point, 2),
        "M_total": round(M_udl + M_point, 2),
    }

# ──────────────────────────────────────────────
#  Maximum Bending Moment
# ──────────────────────────────────────────────

def bending_moment(load, span, beam_type="simply_supported", load_type="udl",
                   load_position=None, overhang_length=0):
    """
    Calculate maximum bending moment (kNm).
    load: kN/m for UDL/triangular, kN for point load
    span: m (distance between supports A and B)
    beam_type: simply_supported | cantilever | continuous | overhang
    load_type: udl | point_load | triangular
    load_position: distance from left support (m) for point load
    overhang_length: length of overhang beyond support B (m)
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    if beam_type == "simply_supported":
        if load_type == "point_load":
            a = load_position
            return load * a * (span - a) / span
        elif load_type == "triangular":
            # Triangular: 0 at left → w_max at right
            # M_max = wL² / (9√3)
            return (load * span**2) / (9 * math.sqrt(3))
        else:  # udl
            return (load * span**2) / 8

    elif beam_type == "cantilever":
        if load_type == "point_load":
            return load * load_position
        elif load_type == "triangular":
            # w_max at fixed end, 0 at free end
            return (load * span**2) / 6
        else:  # udl
            return (load * span**2) / 2

    elif beam_type == "continuous":
        if load_type == "point_load":
            a = load_position
            return load * a * (span - a) / span * 0.8
        elif load_type == "triangular":
            return (load * span**2) / (9 * math.sqrt(3)) * 0.75
        else:  # udl
            return (load * span**2) / 12

    elif beam_type == "overhang":
        oh = overhang_length
        if load_type == "point_load":
            # Point load at distance 'a' from support A
            a = load_position
            if a <= span:
                # Load on the main span: M_max = Wab/L at the load point
                return load * a * (span - a) / span
            else:
                # Load on the overhang: M_max = P × overhang at support B
                return load * (a - span)
        elif load_type == "udl":
            # UDL over full length (L + overhang)
            total_len = span + oh
            R_B = load * total_len**2 / (2 * span)
            R_A = load * total_len - R_B
            # Max hogging moment at B = -w × oh² / 2
            M_at_B = abs(load * oh**2 / 2)
            # Max sagging moment in span (at x where V=0)
            if R_A > 0:
                x_zero_shear = R_A / load
                M_sag = R_A * x_zero_shear - load * x_zero_shear**2 / 2
            else:
                M_sag = 0
            return max(M_at_B, M_sag)
        else:
            return (load * span**2) / 8

    # Fallback
    return (load * span**2) / 8


# ──────────────────────────────────────────────
#  Maximum Shear Force
# ──────────────────────────────────────────────

def max_shear_force(load, span, beam_type="simply_supported", load_type="udl",
                    load_position=None, overhang_length=0):
    """
    Calculate maximum shear force (kN).
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    if beam_type == "simply_supported":
        if load_type == "point_load":
            a = load_position
            return max(load * (span - a) / span, load * a / span)
        elif load_type == "triangular":
            return load * span / 3  # R_B (larger reaction)
        else:
            return load * span / 2

    elif beam_type == "cantilever":
        if load_type == "point_load":
            return load
        elif load_type == "triangular":
            return load * span / 2
        else:
            return load * span

    elif beam_type == "continuous":
        if load_type == "point_load":
            a = load_position
            return max(load * (span - a) / span, load * a / span)
        elif load_type == "triangular":
            return load * span / 3
        else:
            return load * span / 2

    elif beam_type == "overhang":
        oh = overhang_length
        if load_type == "point_load":
            a = load_position
            if a > span:
                # Point load on overhang: R_B = P(a)/L, R_A = P - R_B
                R_B = load * a / span
                R_A = load - R_B  # can be negative
                return max(abs(R_A), abs(R_B), load)
            else:
                return max(load * (span - a) / span, load * a / span)
        elif load_type == "udl":
            total_len = span + oh
            R_B = load * total_len**2 / (2 * span)
            R_A = load * total_len - R_B
            return max(abs(R_A), abs(R_B))
        else:
            return load * span / 2

    return load * span / 2


# ──────────────────────────────────────────────
#  Diagram Data Generation (V(x), M(x))
# ──────────────────────────────────────────────

def generate_diagrams(load, span, beam_type="simply_supported", load_type="udl",
                      load_position=None, overhang_length=0):
    """
    Generate x, shear, moment, and load arrays for plotting.
    For overhang beams, diagrams extend over the full length (span + overhang).
    Returns (x_vals, shear_vals, moment_vals, load_vals)
    """
    if load_position is None:
        load_position = span if beam_type == "cantilever" else span / 2

    # Total length for diagram generation
    total_length = span + overhang_length if beam_type == "overhang" else span

    x_vals = []
    shear_vals = []
    moment_vals = []
    load_vals = []
    steps = 40
    dx = total_length / steps

    for i in range(steps + 1):
        x = round(i * dx, 4)
        shear, moment, load_val = _compute_point(
            x, load, span, beam_type, load_type, load_position, overhang_length
        )
        x_vals.append(round(x, 3))
        shear_vals.append(round(shear, 3))
        moment_vals.append(round(moment, 3))
        load_vals.append(round(load_val, 3))

    return x_vals, shear_vals, moment_vals, load_vals


def _compute_point(x, load, span, beam_type, load_type, load_position, overhang_length=0):
    """Compute shear, moment, and load intensity at position x."""

    # ── Simply Supported ──
    if beam_type == "simply_supported":
        if load_type == "udl":
            shear = load * span / 2 - load * x
            moment = load * x * (span - x) / 2
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            R_A = load * (span - a) / span
            if x < a:
                return R_A, R_A * x, 0
            else:
                return R_A - load, R_A * x - load * (x - a), 0

        elif load_type == "triangular":
            # 0 at left → w_max at right. w(x) = w*x/L
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = R_A * x - load * x**3 / (6 * span)
            return shear, moment, load * x / span

    # ── Cantilever (fixed at left x=0, free at right x=L) ──
    elif beam_type == "cantilever":
        if load_type == "udl":
            shear = load * (span - x)
            moment = load * (span - x)**2 / 2
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            if x <= a:
                return load, load * (a - x), 0
            else:
                return 0, 0, 0

        elif load_type == "triangular":
            # w_max at fixed end → 0 at free end. w(x) = w*(L-x)/L
            shear = load * (span - x)**2 / (2 * span)
            moment = load * (span - x)**3 / (6 * span)
            return shear, moment, load * (span - x) / span

    # ── Continuous (simplified with reduction factors) ──
    elif beam_type == "continuous":
        if load_type == "udl":
            shear = load * span / 2 - load * x
            moment = load * x * (span - x) / 2 * 0.75
            return shear, moment, load

        elif load_type == "point_load":
            a = load_position
            R_A = load * (span - a) / span
            if x < a:
                return R_A, R_A * x * 0.8, 0
            else:
                return R_A - load, (R_A * x - load * (x - a)) * 0.8, 0

        elif load_type == "triangular":
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = (R_A * x - load * x**3 / (6 * span)) * 0.75
            return shear, moment, load * x / span

    # ── Overhang (supported at A=0 and B=span, overhang from B to span+oh) ──
    elif beam_type == "overhang":
        oh = overhang_length
        total_len = span + oh

        if load_type == "point_load":
            a = load_position  # load position from A
            # Reactions: ΣM_A=0 → R_B×L = P×a → R_B = Pa/L
            R_B = load * a / span
            R_A = load - R_B

            if x < min(a, span):  # Before load and before B
                return R_A, R_A * x, 0
            elif x < span and x >= a:  # After load, before B
                return R_A - load, R_A * x - load * (x - a), 0
            elif x == span:  # At support B (just before)
                V_before_B = R_A - (load if a <= span else 0)
                M_at_B = R_A * span - (load * (span - a) if a <= span else 0)
                return V_before_B, M_at_B, 0
            else:  # On the overhang (x > span)
                if a <= span:
                    # Load was on the main span, no load on overhang
                    shear = R_A - load + R_B  # = 0
                    moment = R_A * x - load * (x - a) + R_B * (x - span)
                else:
                    # Load is on the overhang at distance a from A
                    if x < a:
                        shear = R_A + R_B  # = load (carried to overhang)
                        moment = R_A * x + R_B * (x - span)
                    else:
                        shear = R_A + R_B - load  # = 0
                        moment = R_A * x + R_B * (x - span) - load * (x - a)
                return shear, moment, 0

        elif load_type == "udl":
            # UDL over full length (span + overhang)
            R_B = load * total_len**2 / (2 * span)
            R_A = load * total_len - R_B

            if x <= span:
                shear = R_A - load * x
                moment = R_A * x - load * x**2 / 2
            else:
                shear = R_A - load * x + R_B
                moment = R_A * x - load * x**2 / 2 + R_B * (x - span)
            return shear, moment, load

        elif load_type == "triangular":
            R_A = load * span / 6
            shear = R_A - load * x**2 / (2 * span)
            moment = R_A * x - load * x**3 / (6 * span)
            return shear, moment, load * x / span

    # Fallback: simply supported UDL
    shear = load * span / 2 - load * x
    moment = load * x * (span - x) / 2
    return shear, moment, load


# ──────────────────────────────────────────────
#  MULTI-LOAD Superposition Functions
# ──────────────────────────────────────────────

def design_moment_multi(loads_list, span, beam_type="simply_supported",
                        overhang_length: float = 0.0, beam_self_weight_udl: float = 0.0):
    """
    Calculate total design moment from multiple loads using superposition.

    loads_list: list of dicts, each with:
        {"type": "udl", "w": <kN/m>, "start": <m>, "end": <m>}
        {"type": "point_load", "P": <kN>, "a": <m>}

    beam_self_weight_udl: additional full-span UDL from self-weight + wall (kN/m)

    Returns dict with M_total and per-load contributions.
    """
    contributions = []
    M_total = 0.0

    # Add beam self-weight as full-span UDL
    if beam_self_weight_udl > 0:
        M_sw = bending_moment(beam_self_weight_udl, span, beam_type, "udl",
                              overhang_length=overhang_length)
        contributions.append({"desc": "Self-weight + wall UDL", "M": round(M_sw, 2)})
        M_total += M_sw

    for i, ld in enumerate(loads_list):
        if ld["type"] == "udl":
            w = ld["w"]
            start = ld.get("start")
            end = ld.get("end")

            if start is not None and end is not None:
                # Partial UDL
                M_i = _partial_udl_moment(w, start, end, span, beam_type, overhang_length)
            else:
                # Full-span UDL
                M_i = bending_moment(w, span, beam_type, "udl",
                                     overhang_length=overhang_length)
            label = f"UDL {w} kN/m"
            if start is not None:
                label += f" ({start}m–{end}m)"

        elif ld["type"] == "point_load":
            P = ld["P"]
            a = ld.get("a") or (span / 2)
            M_i = bending_moment(P, span, beam_type, "point_load", a, overhang_length)
            label = f"Point load {P} kN at {a}m"

        else:
            continue

        contributions.append({"desc": label, "M": round(M_i, 2)})
        M_total += M_i

    return {
        "M_total": round(M_total, 2),
        "contributions": contributions,
    }


def max_shear_force_multi(loads_list, span, beam_type="simply_supported",
                          overhang_length: float = 0.0, beam_self_weight_udl: float = 0.0):
    """
    Calculate maximum shear force from multiple loads using superposition.
    """
    V_total = 0.0

    if beam_self_weight_udl > 0:
        V_total += max_shear_force(beam_self_weight_udl, span, beam_type, "udl",
                                    overhang_length=overhang_length)

    for ld in loads_list:
        if ld["type"] == "udl":
            w = ld["w"]
            start = ld.get("start")
            end = ld.get("end")
            if start is not None and end is not None:
                V_total += _partial_udl_max_shear(w, start, end, span, beam_type, overhang_length)
            else:
                V_total += max_shear_force(w, span, beam_type, "udl",
                                            overhang_length=overhang_length)
        elif ld["type"] == "point_load":
            P = ld["P"]
            a = ld.get("a") or (span / 2)
            V_total += max_shear_force(P, span, beam_type, "point_load", a, overhang_length)

    return round(V_total, 3)


def generate_diagrams_multi(loads_list, span, beam_type="simply_supported",
                            overhang_length: float = 0.0, beam_self_weight_udl: float = 0.0):
    """
    Generate superposed V(x), M(x), load(x) arrays from multiple loads.
    Uses superposition: compute each load independently and sum.
    """
    total_length = span + overhang_length if beam_type == "overhang" else span
    steps = 40
    dx = total_length / steps

    # Initialize arrays
    x_vals = [round(i * dx, 3) for i in range(steps + 1)]
    shear_total = [0.0] * (steps + 1)
    moment_total = [0.0] * (steps + 1)
    load_total = [0.0] * (steps + 1)

    # ── Self-weight / wall UDL (always full-span) ──
    if beam_self_weight_udl > 0:
        for j, x in enumerate(x_vals):
            s, m, l = _compute_point(x, beam_self_weight_udl, span, beam_type, "udl",
                                      span / 2, overhang_length)
            shear_total[j] += s
            moment_total[j] += m
            load_total[j] += l

    # ── Each user load ──
    for ld in loads_list:
        if ld["type"] == "udl":
            w = ld["w"]
            start = ld.get("start")
            end = ld.get("end")

            if start is not None and end is not None:
                # Partial UDL: compute analytically
                for j, x in enumerate(x_vals):
                    s, m, l = _compute_partial_udl_point(x, w, start, end, span,
                                                          beam_type, overhang_length)
                    shear_total[j] += s
                    moment_total[j] += m
                    load_total[j] += l
            else:
                # Full-span UDL
                for j, x in enumerate(x_vals):
                    s, m, l = _compute_point(x, w, span, beam_type, "udl",
                                              span / 2, overhang_length)
                    shear_total[j] += s
                    moment_total[j] += m
                    load_total[j] += l

        elif ld["type"] == "point_load":
            P = ld["P"]
            a = ld.get("a") or (span / 2)
            for j, x in enumerate(x_vals):
                s, m, _ = _compute_point(x, P, span, beam_type, "point_load",
                                          a, overhang_length)
                shear_total[j] += s
                moment_total[j] += m

    # Round results
    shear_total = [round(v, 3) for v in shear_total]
    moment_total = [round(v, 3) for v in moment_total]
    load_total = [round(v, 3) for v in load_total]

    return x_vals, shear_total, moment_total, load_total


def _partial_udl_moment(w, start, end, span, beam_type, overhang_length=0):
    """
    Maximum bending moment for a partial UDL from 'start' to 'end' on a simply supported beam.
    Uses equilibrium: R_A = w*(end-start)*(span - (start+end)/2) / span
    M_max is found at the point of zero shear within the loaded region.
    """
    if beam_type != "simply_supported":
        # For non-simply-supported, approximate using full-span fraction
        frac = (end - start) / span
        full_M = bending_moment(w, span, beam_type, "udl", overhang_length=overhang_length)
        return full_M * frac

    c = end - start  # length of loaded region
    centre = (start + end) / 2
    R_A = w * c * (span - centre) / span

    # Zero shear at x0 from A (within loaded region)
    # V(x) = R_A - w*(x - start) = 0 for start <= x <= end
    x0 = start + R_A / w
    if x0 < start:
        x0 = start
    if x0 > end:
        x0 = end

    # Moment at x0
    M = R_A * x0 - w * (x0 - start)**2 / 2
    return abs(M)


def _partial_udl_max_shear(w, start, end, span, beam_type, overhang_length=0):
    """Max shear from a partial UDL on a simply supported beam."""
    if beam_type != "simply_supported":
        frac = (end - start) / span
        full_V = max_shear_force(w, span, beam_type, "udl", overhang_length=overhang_length)
        return full_V * frac

    c = end - start
    centre = (start + end) / 2
    R_A = w * c * (span - centre) / span
    R_B = w * c - R_A
    return max(abs(R_A), abs(R_B))


def _compute_partial_udl_point(x, w, start, end, span, beam_type, overhang_length=0):
    """
    Compute V, M, load_intensity at position x for a partial UDL
    on a simply supported beam.
    """
    if beam_type != "simply_supported":
        # Approximate: only apply load intensity within [start, end]
        if start <= x <= end:
            load_val = w
        else:
            load_val = 0
        # Use full-span method with zero outside range
        c = end - start
        centre = (start + end) / 2
        total_load = w * c
        R_A = total_load * (span - centre) / span

        if x < start:
            V = R_A
            M = R_A * x
        elif x <= end:
            V = R_A - w * (x - start)
            M = R_A * x - w * (x - start)**2 / 2
        else:
            R_B = total_load - R_A
            V = R_A - w * c  # = -R_B
            M = R_A * x - w * c * (x - start - c / 2)
        return V, M, load_val

    # Simply supported
    c = end - start
    centre = (start + end) / 2
    total_load = w * c
    R_A = total_load * (span - centre) / span

    if start <= x <= end:
        load_val = w
    else:
        load_val = 0

    if x < start:
        V = R_A
        M = R_A * x
    elif x <= end:
        V = R_A - w * (x - start)
        M = R_A * x - w * (x - start)**2 / 2
    else:
        V = R_A - total_load  # = -R_B
        M = R_A * x - total_load * (x - centre)

    return V, M, load_val


# ──────────────────────────────────────────────
#  Shear Force (single point — legacy)
# ──────────────────────────────────────────────

def shear_force(load, span, x):
    """
    Calculate shear force at distance x from the support (kN)
    load: kN/m
    span: m
    x: m
    """
    return (load * span) / 2 - load * x


# ──────────────────────────────────────────────
#  BS 8110 Bending Reinforcement Design
# ──────────────────────────────────────────────

# Cover assumption: 25mm cover + 8mm link + half bar ≈ 40mm
DEFAULT_COVER = 25   # mm
DEFAULT_LINK = 8     # mm
DEFAULT_BAR  = 16    # mm (assumed main bar for effective depth calc)


def effective_depth(total_depth_mm, cover=DEFAULT_COVER, link=DEFAULT_LINK, bar=DEFAULT_BAR):
    """
    Calculate effective depth d = h - cover - link - bar/2
    Returns d in mm.
    """
    return total_depth_mm - cover - link - bar / 2


def design_bending_reinforcement(M_kNm, b_mm, h_mm, fcu, fy,
                                  cover=DEFAULT_COVER, link=DEFAULT_LINK, bar=DEFAULT_BAR):
    """
    BS 8110 bending reinforcement design for a singly reinforced section.

    Parameters:
    -----------
    M_kNm  : design moment (kNm) — always use the absolute value
    b_mm   : beam width (mm)
    h_mm   : beam total depth (mm)
    fcu    : concrete cube strength (N/mm²)
    fy     : steel yield strength (N/mm²)
    cover  : concrete cover to links (mm)
    link   : link diameter (mm)
    bar    : assumed main bar diameter (mm)

    Returns:
    --------
    dict with:
        M        : design moment (kNm)
        Mu       : moment of resistance (kNm)
        adequate : True if M ≤ Mu (section is adequate)
        d        : effective depth (mm)
        K        : M / (fcu × b × d²)  — capped at 0.156
        z        : lever arm (mm) — capped at 0.95d
        As_req   : required steel area (mm²)
        message  : human-readable status
    """
    M = abs(M_kNm)
    b = b_mm
    d = effective_depth(h_mm, cover, link, bar)

    # ── Step 1: Moment of resistance ──
    # Mu = 0.156 × fcu × b × d²  (for balanced/max singly reinforced section)
    Mu_Nmm = 0.156 * fcu * b * d**2
    Mu_kNm = Mu_Nmm / 1e6

    adequate = M <= Mu_kNm

    # ── Step 2: K constant ──
    M_Nmm = M * 1e6
    K = M_Nmm / (fcu * b * d**2)

    # K must not exceed 0.156 (singly reinforced limit)
    K_used = min(K, 0.156)

    # ── Step 3: Lever arm z ──
    inner = 0.25 - K_used / 0.9
    if inner < 0:
        inner = 0  # safety fallback
    z = d * (0.5 + math.sqrt(inner))

    # z must not exceed 0.95d
    z = min(z, 0.95 * d)

    # ── Step 4: Area of steel As ──
    As_req = M_Nmm / (0.95 * fy * z)

    message = "Section adequate (M <= Mu)" if adequate else \
              f"Section inadequate (M={M:.1f} > Mu={Mu_kNm:.1f}). Increase beam section."

    return {
        "M": round(M, 2),
        "Mu": round(Mu_kNm, 2),
        "adequate": adequate,
        "d": round(d, 1),
        "K": round(K, 5),
        "K_used": round(K_used, 5),
        "z": round(z, 2),
        "As_req": round(As_req, 2),
        "message": message,
    }


def design_reinforcement_with_resize(M_kNm, b_mm, h_mm, fcu, fy):
    """
    Design bending reinforcement, automatically increasing beam section
    if the design moment exceeds the moment of resistance.

    Tries increasing depth first, then width, following standard progressions.

    Returns (reinforcement_result, final_width, final_depth, resized)
    """
    width = b_mm
    depth = h_mm

    for w in STANDARD_WIDTHS:
        if w < width:
            continue
        for d in STANDARD_DEPTHS:
            if d < depth and w == width:
                continue
            result = design_bending_reinforcement(M_kNm, w, d, fcu, fy)
            if result["adequate"]:
                resized = (w != b_mm or d != h_mm)
                return result, w, d, resized

    # Fallback: use largest size available
    result = design_bending_reinforcement(
        M_kNm, STANDARD_WIDTHS[-1], STANDARD_DEPTHS[-1], fcu, fy
    )
    return result, STANDARD_WIDTHS[-1], STANDARD_DEPTHS[-1], True


def steel_area(Mu, fy, d):
    """
    Calculate steel area (mm²) — legacy/simplified.
    Mu: bending moment (kNm)
    fy: yield strength (MPa)
    d: effective depth (mm)
    """
    Mu_Nmm = Mu * 1e6  # convert kNm to Nmm
    z = 0.9 * d
    return Mu_Nmm / (0.87 * fy * z)


def design_beam(load, span, fy=500, d=450):
    """Legacy helper — kept for backward compatibility."""
    Mu = bending_moment(load, span)
    As = steel_area(Mu, fy, d)
    return {
        "bending_moment": round(Mu, 2),
        "steel_area": round(As, 2)
    }



# ──────────────────────────────────────────────
#  Reinforcement Recommendation
# ──────────────────────────────────────────────

def recommend_reinforcement(As_required):
    bar_sizes = [10, 12, 16, 20, 25]

    solutions = []

    for d in bar_sizes:
        area_bar = (math.pi * d**2) / 4

        num_bars = math.ceil(As_required / area_bar)

        provided_area = num_bars * area_bar

        solutions.append({
            "diameter": d,
            "bars": num_bars,
            "provided_area": round(provided_area, 2)
        })

    # Pick best (least excess area that still meets the requirement)
    valid = [s for s in solutions if s["provided_area"] >= As_required]
    if valid:
        best = min(valid, key=lambda x: x["provided_area"])
    else:
        # Fallback: if none meet it exactly (shouldn't happen), pick the largest
        best = max(solutions, key=lambda x: x["provided_area"])

    return best, solutions


# ──────────────────────────────────────────────
#  Beam Size Estimation (Standard Sizes)
# ──────────────────────────────────────────────

# Standard width progression: 230 → 300 → 450 → 600 → 750 → 900 ...
#   (first increase +70mm, then consistent +150mm)
STANDARD_WIDTHS = [230, 300, 450, 600, 750, 900, 1050, 1200]

# Standard depth progression: 300 → 450 → 600 → 750 → 900 → 1050 → 1200 ...
#   (consistent increase of 150mm)
STANDARD_DEPTHS = [300, 450, 600, 750, 900, 1050, 1200, 1350, 1500]

# Span/depth ratio limits per beam type
_DEFLECTION_LIMITS = {
    "simply_supported": 20,
    "cantilever": 7,
    "continuous": 26,
    "overhang": 20,
}


def estimate_beam_size(span, beam_type="simply_supported"):
    """
    Select the smallest standard beam width and depth that satisfies
    the span-to-depth deflection limit for the given beam type.

    Width progression : 230, 300, 450, 600, 750, 900 … mm
    Depth progression : 300, 450, 600, 750, 900, 1050, 1200 … mm
    """
    limit = _DEFLECTION_LIMITS.get(beam_type, 20)
    min_depth = (span * 1000) / limit   # required minimum depth (mm)

    # Pick the smallest standard depth that satisfies the deflection limit
    depth = STANDARD_DEPTHS[-1]  # fallback to largest
    for d in STANDARD_DEPTHS:
        if d >= min_depth:
            depth = d
            break

    # Pick the smallest standard width ≥ half the depth (common practice)
    half_depth = depth * 0.5
    width = STANDARD_WIDTHS[-1]  # fallback to largest
    for w in STANDARD_WIDTHS:
        if w >= half_depth:
            width = w
            break

    # Ensure minimum width of 230mm
    width = max(width, 230)

    return {
        "width": width,
        "depth": depth
    }


# ──────────────────────────────────────────────
#  BS 8110 Deflection Check (Table 3.9)
# ──────────────────────────────────────────────

# Table 3.9 — Basic span/effective depth ratios
_BASIC_SPAN_DEPTH_RATIOS = {
    "cantilever":        7,
    "simply_supported": 20,
    "continuous":       26,
    "overhang":         20,
}


def check_deflection_bs8110(span_m, b_mm, h_mm, M_kNm, As_req, As_prov,
                             fy, beam_type="simply_supported", beta_b=1.0):
    """
    BS 8110 deflection check using Table 3.9, service stress & modification factor.

    Parameters:
    -----------
    span_m   : beam span (m)
    b_mm     : beam width (mm)
    h_mm     : beam total depth (mm)
    M_kNm    : design moment (kNm) — the major moment for the span
    As_req   : required area of steel (mm²)
    As_prov  : provided area of steel (mm²)
    fy       : steel yield strength (N/mm²)
    beam_type: "simply_supported", "cantilever", "continuous", "overhang"
    beta_b   : ratio of redistributed moment to elastic moment (default 1.0)

    Returns:
    --------
    dict with:
        status       : "SAFE" or "NOT SAFE"
        basic_ratio  : basic span/d ratio from Table 3.9
        actual_ratio : actual span/d ratio
        allowable_ratio : basic_ratio × MF
        fs           : service stress (N/mm²)
        MF           : modification factor (capped at 2.0)
        MF_uncapped  : raw modification factor before capping
        d            : effective depth (mm)
        message      : human-readable result
    """
    M = abs(M_kNm)
    d = effective_depth(h_mm)
    b = b_mm

    # ── Table 3.9: Basic span/effective depth ratio ──
    basic_ratio = _BASIC_SPAN_DEPTH_RATIOS.get(beam_type, 20)

    # ── Service Stress (fs) ──
    # fs = (2/3) × fy × (As_req / As_prov) × (1 / βb)
    if As_prov > 0:
        fs = (2.0 / 3.0) * fy * (As_req / As_prov) * (1.0 / beta_b)
    else:
        fs = (2.0 / 3.0) * fy

    # ── Modification Factor (MF) ──
    # MF = 0.55 + (477 - fs) / [120 × (0.9 + M/(bd²))]
    M_Nmm = M * 1e6
    denominator = 120.0 * (0.9 + M_Nmm / (b * d**2))
    if denominator > 0:
        MF_raw = 0.55 + (477.0 - fs) / denominator
    else:
        MF_raw = 2.0

    # MF must not be greater than 2.0
    MF = min(MF_raw, 2.0)

    # ── Deflection Check ──
    actual_ratio = (span_m * 1000) / d
    allowable_ratio = basic_ratio * MF

    if actual_ratio <= allowable_ratio:
        status = "SAFE"
        message = (f"Deflection OK: actual span/d = {actual_ratio:.2f} ≤ "
                   f"allowable = {allowable_ratio:.2f} "
                   f"(basic {basic_ratio} × MF {MF:.3f})")
    else:
        status = "NOT SAFE"
        message = (f"Deflection FAILS: actual span/d = {actual_ratio:.2f} > "
                   f"allowable = {allowable_ratio:.2f} "
                   f"(basic {basic_ratio} × MF {MF:.3f}). "
                   f"Increase As_prov or beam depth.")

    return {
        "status": status,
        "basic_ratio": basic_ratio,
        "actual_ratio": round(actual_ratio, 2),
        "allowable_ratio": round(allowable_ratio, 2),
        "fs": round(fs, 2),
        "MF": round(MF, 4),
        "MF_uncapped": round(MF_raw, 4),
        "d": round(d, 1),
        "message": message,
    }


def deflection_check_with_fix(span_m, b_mm, h_mm, M_kNm, As_req, As_prov_initial,
                               fy, fcu, beam_type="simply_supported"):
    """
    Perform BS 8110 deflection check and attempt fixes if it fails.

    Strategy:
    1. Check deflection with current As_prov
    2. If MF > 2.0 or deflection fails: try increasing As_prov (next bar size up)
    3. If still failing: increase beam depth and recalculate

    Returns:
    --------
    (deflection_result, As_prov_final, h_final, reinf_recommendation, was_fixed)
    """
    As_prov = As_prov_initial
    h = h_mm

    # ── Attempt 1: Check with current reinforcement ──
    result = check_deflection_bs8110(span_m, b_mm, h, M_kNm, As_req, As_prov,
                                      fy, beam_type)

    if result["status"] == "SAFE":
        best_reinf, options = recommend_reinforcement(As_prov)
        return result, As_prov, h, best_reinf, False

    # ── Attempt 2: Increase As_prov (try larger bar combinations) ──
    # Progressively increase As_prov by trying multiples until MF ≤ 2 and deflection passes
    bar_sizes = [10, 12, 16, 20, 25, 32]
    for diameter in bar_sizes:
        area_bar = (math.pi * diameter**2) / 4
        for num_bars in range(1, 15):
            trial_As = num_bars * area_bar
            if trial_As < As_req:
                continue  # must at least meet As_req
            trial_result = check_deflection_bs8110(
                span_m, b_mm, h, M_kNm, As_req, trial_As, fy, beam_type
            )
            if trial_result["status"] == "SAFE":
                best_reinf, options = recommend_reinforcement(trial_As)
                return trial_result, trial_As, h, best_reinf, True

    # ── Attempt 3: Increase beam depth ──
    for new_depth in STANDARD_DEPTHS:
        if new_depth <= h:
            continue
        # Recalculate reinforcement for new depth
        reinf = design_bending_reinforcement(M_kNm, b_mm, new_depth, fcu, fy)
        new_As_req = reinf["As_req"]
        best_reinf, options = recommend_reinforcement(new_As_req)
        new_As_prov = best_reinf["provided_area"]

        trial_result = check_deflection_bs8110(
            span_m, b_mm, new_depth, M_kNm, new_As_req, new_As_prov,
            fy, beam_type
        )
        if trial_result["status"] == "SAFE":
            return trial_result, new_As_prov, new_depth, best_reinf, True

    # Fallback: return the last result even if failing
    result = check_deflection_bs8110(span_m, b_mm, h, M_kNm, As_req, As_prov,
                                      fy, beam_type)
    best_reinf, options = recommend_reinforcement(As_prov)
    return result, As_prov, h, best_reinf, False


# ──────────────────────────────────────────────
#  BS 8110 Shear Reinforcement Design
# ──────────────────────────────────────────────

# Standard link (stirrup) bar diameters
LINK_DIAMETERS = [8, 10, 12]


def concrete_shear_capacity(b_mm, d_mm, As_prov, fcu):
    """
    Calculate concrete shear capacity vc per BS 8110 Table 3.8.
    
    vc = 0.79 × (100As / bd)^(1/3) × (400/d)^(1/4) / γm
    
    Where:
    - 100As/bd should not exceed 3
    - (400/d)^(1/4) should not be less than 0.67 (when d > 400mm, use 1.0 for conservative)
    - γm = 1.25 (partial safety factor for concrete in shear)
    - fcu factor: multiply by (fcu/25)^(1/3), but fcu should not exceed 40 N/mm²
    
    Returns vc in N/mm²
    """
    gamma_m = 1.25

    # 100As/bd — capped at 3
    rho = min(100 * As_prov / (b_mm * d_mm), 3.0)

    # (400/d)^(1/4) — not less than 0.67
    if d_mm <= 400:
        depth_factor = (400 / d_mm) ** 0.25
    else:
        depth_factor = max((400 / d_mm) ** 0.25, 0.67)

    # fcu factor — capped at 40 N/mm²
    fcu_used = min(fcu, 40)
    fcu_factor = (fcu_used / 25) ** (1 / 3)

    vc = (0.79 * (rho ** (1 / 3)) * depth_factor * fcu_factor) / gamma_m

    return round(vc, 4)


def design_shear_reinforcement(V_kN, b_mm, h_mm, As_prov, fcu, fy_v=460):
    """
    Design shear reinforcement (stirrups/links) per BS 8110 Clause 3.4.5.
    
    Parameters:
    -----------
    V_kN    : Ultimate shear force (kN)
    b_mm    : Beam width (mm)
    h_mm    : Total beam depth (mm)
    As_prov : Area of longitudinal tension steel provided (mm²)
    fcu     : Characteristic cube strength of concrete (N/mm²)
    fy_v    : Characteristic strength of link reinforcement (N/mm²), default 460
    
    Returns:
    --------
    dict with full shear design breakdown
    """
    d = effective_depth(h_mm)
    V = V_kN * 1000  # Convert kN to N

    # ── Step 1: Calculate shear stress ──
    v = V / (b_mm * d)  # N/mm²

    # ── Step 2: Check ultimate shear limit ──
    # v must not exceed 0.8√fcu or 5 N/mm², whichever is smaller
    v_max = min(0.8 * math.sqrt(fcu), 5.0)
    if v > v_max:
        return {
            "V_kN": round(V_kN, 2),
            "d": round(d, 2),
            "v": round(v, 4),
            "v_max": round(v_max, 4),
            "vc": 0,
            "status": "FAIL",
            "message": f"Shear stress v = {v:.2f} N/mm² exceeds v_max = {v_max:.2f} N/mm² — increase beam section",
            "links_required": False,
            "link_diameter": 0,
            "link_spacing": 0,
            "Asv_req": 0,
            "Asv_prov": 0,
            "link_description": "Section inadequate — increase beam size",
        }

    # ── Step 3: Calculate concrete shear capacity ──
    vc = concrete_shear_capacity(b_mm, d_mm=d, As_prov=As_prov, fcu=fcu)

    # ── Step 4: Determine shear reinforcement requirement ──
    # Case 1: v < 0.5vc → Minimum links (nominal)
    # Case 2: 0.5vc ≤ v ≤ (vc + 0.4) → Minimum links
    # Case 3: v > (vc + 0.4) → Design links required

    if v < 0.5 * vc:
        # Nominal links — very low shear
        # Minimum links: Asv/sv >= 0.4b / (0.87 × fyv)
        Asv_sv_min = (0.4 * b_mm) / (0.87 * fy_v)
        link_result = _select_links(Asv_sv_min, d, b_mm)
        return {
            "V_kN": round(V_kN, 2),
            "d": round(d, 2),
            "v": round(v, 4),
            "v_max": round(v_max, 4),
            "vc": round(vc, 4),
            "status": "SAFE",
            "message": f"v = {v:.2f} < 0.5vc = {0.5*vc:.2f} N/mm² — minimum (nominal) links provided",
            "links_required": True,
            "link_diameter": link_result["diameter"],
            "link_spacing": link_result["spacing"],
            "Asv_sv_req": round(Asv_sv_min, 4),
            "Asv_prov": round(link_result["Asv"], 2),
            "link_description": link_result["description"],
            "link_type": "nominal",
        }

    elif v <= (vc + 0.4):
        # Minimum links
        # Asv/sv >= 0.4b / (0.87 × fyv)
        Asv_sv_min = (0.4 * b_mm) / (0.87 * fy_v)
        link_result = _select_links(Asv_sv_min, d, b_mm)
        return {
            "V_kN": round(V_kN, 2),
            "d": round(d, 2),
            "v": round(v, 4),
            "v_max": round(v_max, 4),
            "vc": round(vc, 4),
            "status": "SAFE",
            "message": f"v = {v:.2f} ≤ vc + 0.4 = {vc+0.4:.2f} N/mm² — minimum links provided",
            "links_required": True,
            "link_diameter": link_result["diameter"],
            "link_spacing": link_result["spacing"],
            "Asv_sv_req": round(Asv_sv_min, 4),
            "Asv_prov": round(link_result["Asv"], 2),
            "link_description": link_result["description"],
            "link_type": "minimum",
        }

    else:
        # Design links required
        # Asv/sv >= b(v - vc) / (0.87 × fyv)
        Asv_sv_req = (b_mm * (v - vc)) / (0.87 * fy_v)
        link_result = _select_links(Asv_sv_req, d, b_mm)
        return {
            "V_kN": round(V_kN, 2),
            "d": round(d, 2),
            "v": round(v, 4),
            "v_max": round(v_max, 4),
            "vc": round(vc, 4),
            "status": "SAFE",
            "message": f"v = {v:.2f} > vc + 0.4 = {vc+0.4:.2f} N/mm² — design links required",
            "links_required": True,
            "link_diameter": link_result["diameter"],
            "link_spacing": link_result["spacing"],
            "Asv_sv_req": round(Asv_sv_req, 4),
            "Asv_prov": round(link_result["Asv"], 2),
            "link_description": link_result["description"],
            "link_type": "design",
        }


def _select_links(Asv_sv_required, d, b_mm):
    """
    Select appropriate link diameter and spacing.
    
    For 2-legged stirrups: Asv = 2 × π/4 × dia²
    Spacing sv = Asv / (Asv/sv required)
    
    Max spacing = 0.75d (BS 8110 Clause 3.4.5.5)
    
    Returns dict with diameter, spacing, Asv, description
    """
    max_spacing = 0.75 * d

    for dia in LINK_DIAMETERS:
        # Area of 2-legged stirrup
        Asv = 2 * (math.pi * dia ** 2) / 4

        # Required spacing
        sv = Asv / Asv_sv_required

        # Round down to nearest 25mm
        sv = int(sv / 25) * 25
        if sv < 50:
            continue  # Too tight, try larger diameter

        # Cap at max spacing
        sv = min(sv, int(max_spacing / 25) * 25)
        if sv < 50:
            sv = 50

        return {
            "diameter": dia,
            "spacing": sv,
            "Asv": round(Asv, 2),
            "description": f"Y{dia} links @ {sv}mm c/c (2-legged)",
        }

    # Fallback: largest diameter at minimum spacing
    dia = LINK_DIAMETERS[-1]
    Asv = 2 * (math.pi * dia ** 2) / 4
    sv = max(50, int(max_spacing / 25) * 25)
    return {
        "diameter": dia,
        "spacing": sv,
        "Asv": round(Asv, 2),
        "description": f"Y{dia} links @ {sv}mm c/c (2-legged)",
    }