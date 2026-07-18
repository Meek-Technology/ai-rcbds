import re


def extract_parameters(text):
    # ── Span (e.g., "6m" or "span 6m") ──
    span_match = re.search(r'span\s*(?:of\s*)?(\d+\.?\d*)\s*m', text, re.IGNORECASE) or \
                 re.search(r'(\d+\.?\d*)\s*m\b(?!\s*(?:Pa|pa|height|thick))', text)

    # ── Multiple spans (e.g., "spans 6m, 5m, 4m" or "spans 6m 5m 4m") ──
    multi_span_match = re.search(
        r'spans?\s+(\d+\.?\d*)\s*m[\s,]+(\d+\.?\d*)\s*m(?:[\s,]+(\d+\.?\d*)\s*m)?(?:[\s,]+(\d+\.?\d*)\s*m)?(?:[\s,]+(\d+\.?\d*)\s*m)?',
        text, re.IGNORECASE
    )

    # ── Number of spans (e.g., "3-span" or "3 span" or "three span") ──
    n_span_match = re.search(r'(\d+)[\s-]*span', text, re.IGNORECASE)

    # ── Multiple support types (e.g., "supports: pinned, fixed, roller, pinned") ──
    multi_support_match = re.search(
        r'supports?\s*:?\s*((?:(?:pinned|roller|fixed)[\s,]+){1,}(?:pinned|roller|fixed))',
        text, re.IGNORECASE
    )

    # ── "fixed at A" or "fixed at start" patterns ──
    fixed_start_match = re.search(r'fixed\s+(?:at\s+)?(?:A|start|left|first)', text, re.IGNORECASE)
    fixed_end_match = re.search(r'fixed\s+(?:at\s+)?(?:end|right|last|D|E|F)', text, re.IGNORECASE)


    # ── Load value (e.g., "25kN/m" or "load 25kN/m" or "50kN" for point load) ──
    load_match = re.search(r'(\d+\.?\d*)\s*kN/?m', text, re.IGNORECASE) or \
                 re.search(r'(?:load|udl)\s*(?:of\s*)?(\d+\.?\d*)', text, re.IGNORECASE)

    # ── Point load value (e.g., "point load of 50kN" or "50kN point load") ──
    point_load_match = re.search(r'point\s*load\s*(?:of\s*)?(\d+\.?\d*)\s*kN', text, re.IGNORECASE) or \
                       re.search(r'(\d+\.?\d*)\s*kN\s*point\s*load', text, re.IGNORECASE)

    # ── Load position for point load (e.g., "at 3m" or "at distance 3m") ──
    load_position_match = re.search(r'(?:at|at\s+distance)\s+(\d+\.?\d*)\s*m', text, re.IGNORECASE)

    # ── Concrete strength (e.g., fcu 25 or concrete grade 30) ──
    fcu_match = re.search(r'(?:fcu|fck|concrete\s+grade|grade\s+of\s+concrete)\s*(\d+)', text, re.IGNORECASE)

    # ── Steel strength (e.g., fy 500 or 500 MPa or steel grade 500) ──
    fy_match = re.search(r'(?:fy|steel\s+grade|grade\s+of\s+steel)\s*(\d+)|(\d+)\s*MPa', text, re.IGNORECASE)

    # ── Wall properties ──
    height_match = re.search(r'(?:wall\s+)?height\s*(\d+\.?\d*)', text, re.IGNORECASE)
    thickness_match = re.search(r'(?:wall\s+)?thickness\s*(\d+\.?\d*)', text, re.IGNORECASE)
    density_match = re.search(r'(?:density|unit\s+weight)\s*(\d+\.?\d*)', text, re.IGNORECASE)

    # ── Beam type ──
    beam_type_match = re.search(
        r'(simply\s+supported|cantilever|continuous|overhang(?:ing)?)',
        text, re.IGNORECASE
    )

    # ── Loading type ──
    load_type_match = re.search(
        r'(point\s+load|udl|uniformly\s+distributed|triangular(?:\s+load)?)',
        text, re.IGNORECASE
    )

    # ── Support conditions (left/right) ──
    support_left_match = re.search(
        r'(?:left|start|first)\s+(?:support\s+)?(?:is\s+)?(?:a\s+)?(roller|pinned|fixed)',
        text, re.IGNORECASE
    )
    support_right_match = re.search(
        r'(?:right|end|second)\s+(?:support\s+)?(?:is\s+)?(?:a\s+)?(roller|pinned|fixed|free)',
        text, re.IGNORECASE
    )

    # ── Overhang length (e.g., "overhang BC of 2m", "overhang of 2m", "overhang 2m") ──
    overhang_match = re.search(
        r'overhang(?:\s+\w+)*?\s*(?:of\s+)?(\d+\.?\d*)\s*m',
        text, re.IGNORECASE
    )

    # ── Slab loading (e.g., "slab load 15kN/m" or "slab loading of 20") ──
    slab_load_match = re.search(
        r'slab\s+load(?:ing)?\s*(?:of\s*)?(\d+\.?\d*)\s*(?:kN/?m)?',
        text, re.IGNORECASE
    )

    # ── Process fy (may be in group 1 or group 2) ──
    fy_value = None
    if fy_match:
        fy_value = fy_match.group(1) or fy_match.group(2)

    # ── Determine beam type ──
    beam_type = "simply_supported"
    if beam_type_match:
        raw = beam_type_match.group(1).lower().strip()
        if "simply" in raw:
            beam_type = "simply_supported"
        elif "cantilever" in raw:
            beam_type = "cantilever"
        elif "continuous" in raw:
            beam_type = "continuous"
        elif "overhang" in raw:
            beam_type = "overhang"

    # If an overhang length is mentioned, it's an overhang beam
    # (even if "simply supported" was also mentioned in the prompt)
    if overhang_match:
        beam_type = "overhang"

    # ── Determine load type ──
    load_type = "udl"
    if load_type_match:
        raw = load_type_match.group(1).lower().strip()
        if "point" in raw:
            load_type = "point_load"
        elif "triangular" in raw:
            load_type = "triangular"
        else:
            load_type = "udl"

    # If a point load value was explicitly matched, override load_type
    if point_load_match:
        load_type = "point_load"

    # ── Determine load value ──
    load_value = None
    if load_type == "point_load" and point_load_match:
        load_value = float(point_load_match.group(1))
    elif load_match:
        load_value = float(load_match.group(1))

    # ── Determine support conditions ──
    # Defaults based on beam type
    if beam_type == "cantilever":
        default_left = "fixed"
        default_right = "free"
    elif beam_type == "continuous":
        default_left = "fixed"
        default_right = "pinned"
    elif beam_type == "overhang":
        default_left = "pinned"
        default_right = "roller"
    else:
        default_left = "pinned"
        default_right = "roller"

    support_left = support_left_match.group(1).lower() if support_left_match else default_left
    support_right = support_right_match.group(1).lower() if support_right_match else default_right

    # ── Determine load position ──
    load_pos = float(load_position_match.group(1)) if load_position_match else None
    overhang_len = float(overhang_match.group(1)) if overhang_match else None

    # "free end" detection: if load is at the free end of an overhang,
    # load_position = span + overhang_length
    free_end_match = re.search(r'free\s+end', text, re.IGNORECASE)
    span_val = float(span_match.group(1)) if span_match else None

    if beam_type == "overhang" and free_end_match and overhang_len and span_val:
        load_pos = span_val + overhang_len

    # ── Multi-span extraction (for continuous beams) ──
    spans_list = None
    supports_list = None

    if multi_span_match:
        # Extract all matched span groups (up to 5 spans)
        spans_list = []
        for g in range(1, 6):
            val = multi_span_match.group(g)
            if val:
                spans_list.append(float(val))
        beam_type = "continuous"
        # Use first span as the primary span value
        if spans_list and not span_val:
            span_val = spans_list[0]

    # If continuous but only single span, replicate based on n_span_match
    if beam_type == "continuous" and not spans_list and span_val:
        n_spans = int(n_span_match.group(1)) if n_span_match else 2
        spans_list = [span_val] * n_spans

    # ── Multi-support extraction ──
    if multi_support_match:
        raw_supports = re.findall(r'(pinned|roller|fixed)', multi_support_match.group(1), re.IGNORECASE)
        supports_list = [s.lower() for s in raw_supports]

    # If continuous with spans but no explicit supports, build defaults
    if beam_type == "continuous" and spans_list and not supports_list:
        n_supports = len(spans_list) + 1
        supports_list = ["pinned"] * n_supports
        # Apply fixed end overrides
        if fixed_start_match:
            supports_list[0] = "fixed"
        if fixed_end_match:
            supports_list[-1] = "fixed"

    return {
        "span": span_val,
        "load": load_value,
        "slab_load": float(slab_load_match.group(1)) if slab_load_match else None,
        "point_load": float(point_load_match.group(1)) if point_load_match else 0,
        "fcu": float(fcu_match.group(1)) if fcu_match else None,
        "fy": float(fy_value) if fy_value else None,
        "wall_height": float(height_match.group(1)) if height_match else None,
        "wall_thickness": float(thickness_match.group(1)) if thickness_match else None,
        "density": float(density_match.group(1)) if density_match else None,
        "beam_type": beam_type,
        "load_type": load_type,
        "load_position": load_pos,
        "support_left": support_left,
        "support_right": support_right,
        "overhang_length": overhang_len,
        "spans": spans_list,
        "supports": supports_list,
    }


def apply_defaults(params):
    if not params.get("span"):
        raise ValueError("Span is required but was not provided or could not be parsed.")
    if not params.get("load"):
        raise ValueError("Load is required but was not provided or could not be parsed.")

    return {
        "span": params["span"],
        "load": params["load"],
        "slab_load": params.get("slab_load") or 0,
        "point_load": params.get("point_load") or 0,
        "fcu": params["fcu"] if params["fcu"] else 25.0,
        "fy": params["fy"] if params["fy"] else 460.0,
        "wall_height": params["wall_height"] if params["wall_height"] else 0.0,
        "wall_thickness": params["wall_thickness"] if params["wall_thickness"] else 0.0,
        "density": params["density"] if params["density"] else 2.87,
        "beam_type": params.get("beam_type", "simply_supported"),
        "load_type": params.get("load_type", "udl"),
        "load_position": params.get("load_position"),
        "support_left": params.get("support_left", "pinned"),
        "support_right": params.get("support_right", "roller"),
        "overhang_length": params.get("overhang_length"),
        "spans": params.get("spans"),
        "supports": params.get("supports"),
    }


def normalize_concrete_strength(fcu):
    return fcu  # For now same, but allows future conversion


def calculate_wall_load(density, thickness, height):
    return density * thickness * height