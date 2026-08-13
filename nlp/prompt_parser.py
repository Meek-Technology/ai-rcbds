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

    # ── Overhang length (e.g., "overhang BC of 2m", "overhang of 2m", "overhang 2m", "overhang: 2m") ──
    overhang_match = re.search(
        r'overhang(?:\s*[:=\-]?\s*(?:\w+\s+){0,3})?(?:of\s+)?(\d+\.?\d*)\s*m',
        text, re.IGNORECASE
    )

    # ── Slab loading (e.g., "slab load 15kN/m" or "slab loading of 20") ──
    slab_load_match = re.search(
        r'slab\s+load(?:ing)?\s*(?:of\s*)?(\d+\.?\d*)\s*(?:kN/?m)?',
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

    # ═══════════════════════════════════════════════════
    #  MULTIPLE LOAD EXTRACTION
    # ═══════════════════════════════════════════════════

    loads_list = _extract_loads(text)

    # ── Determine legacy load_type from loads_list ──
    has_udl = any(ld["type"] == "udl" for ld in loads_list)
    has_point = any(ld["type"] == "point_load" for ld in loads_list)

    if has_udl and has_point:
        load_type = "combined"
    elif has_point and not has_udl:
        load_type = "point_load"
    else:
        load_type = "udl"

    # ── Legacy single-load values for backward compatibility ──
    load_value = None
    point_load_value = 0
    load_pos = None

    for ld in loads_list:
        if ld["type"] == "udl" and load_value is None:
            load_value = ld["w"]
        if ld["type"] == "point_load":
            if point_load_value == 0:
                point_load_value = ld["P"]
                load_pos = ld.get("a")
            if load_value is None:
                load_value = ld["P"]

    # Fallback: try legacy single UDL regex if no loads found
    if not loads_list:
        single_load_match = re.search(r'(\d+\.?\d*)\s*kN/?m', text, re.IGNORECASE) or \
                            re.search(r'(?:load|udl)\s*(?:of\s*)?(\d+\.?\d*)', text, re.IGNORECASE)
        if single_load_match:
            load_value = float(single_load_match.group(1))
            loads_list = [{"type": "udl", "w": load_value}]
            load_type = "udl"

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

    # ── Determine load position and overhang ──
    overhang_len = float(overhang_match.group(1)) if overhang_match else None
    span_val = float(span_match.group(1)) if span_match else None

    # "free end" detection: if load is at the free end of an overhang,
    # load_position = span + overhang_length
    free_end_match = re.search(r'free\s+end', text, re.IGNORECASE)
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

    # ── Per-span loads for continuous beams ──
    per_span_loads = None
    if beam_type == "continuous" and spans_list:
        per_span_loads = _extract_per_span_loads(text, len(spans_list))

    return {
        "span": span_val,
        "load": load_value,
        "slab_load": float(slab_load_match.group(1)) if slab_load_match else None,
        "point_load": point_load_value,
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
        "loads": loads_list if loads_list else None,
        "per_span_loads": per_span_loads,
    }


def _extract_loads(text):
    """
    Extract multiple load definitions from a prompt.
    Returns a list of load dicts: [{"type": "udl", "w": ...}, {"type": "point_load", "P": ..., "a": ...}]
    """
    loads = []

    # ── Extract all point loads with positions ──
    # Patterns: "point load 30kN at 2m", "point load of 30kN at 2m", "30kN point load at 2m"
    # Also: "point loads 25kN at 2m and 40kN at 6m"
    pl_patterns = [
        # "point load [of] 30kN at 2m"
        r'point\s+loads?\s*(?:of\s*)?(\d+\.?\d*)\s*kN\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)?',
        # "30kN point load at 2m"
        r'(\d+\.?\d*)\s*kN\s*(?:point\s+load)\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)?',
    ]

    # Find all point load matches
    for pat in pl_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            P = float(m.group(1))
            a = float(m.group(2)) if m.group(2) else None
            loads.append({"type": "point_load", "P": P, "a": a})

    # Deduplicate point loads (same P value from different regex patterns)
    seen_pl = set()
    unique_pl = []
    for ld in loads:
        key = (ld["P"], ld.get("a"))
        if key not in seen_pl:
            seen_pl.add(key)
            unique_pl.append(ld)
    loads = unique_pl

    # ── Extract UDL(s) ──
    # Patterns: "UDL 20kN/m", "UDL of 20kN/m", "20kN/m UDL"
    # Partial: "UDL 20kN/m from 0 to 3m"
    udl_matches = list(re.finditer(
        r'(?:udl|uniformly\s+distributed(?:\s+load)?)\s*(?:of\s*)?(\d+\.?\d*)\s*kN/?m'
        r'(?:\s+from\s+(\d+\.?\d*)\s*m?\s*to\s+(\d+\.?\d*)\s*m)?',
        text, re.IGNORECASE
    ))

    # Also match "20kN/m UDL" pattern
    udl_matches2 = list(re.finditer(
        r'(\d+\.?\d*)\s*kN/m\s*(?:udl|uniformly)',
        text, re.IGNORECASE
    ))

    # Simple "XX kN/m" without "point load" context — only if no explicit UDL match above
    # and no point loads matched for that number
    point_load_values = {ld["P"] for ld in loads}

    if not udl_matches and not udl_matches2:
        # Look for generic kN/m values that aren't point loads
        generic_udl = re.findall(r'(\d+\.?\d*)\s*kN/m', text, re.IGNORECASE)
        for val_str in generic_udl:
            val = float(val_str)
            if val not in point_load_values:
                loads.append({"type": "udl", "w": val})
                break  # Only take first generic UDL

    for m in udl_matches:
        w = float(m.group(1))
        start = float(m.group(2)) if m.group(2) else None
        end = float(m.group(3)) if m.group(3) else None
        ld = {"type": "udl", "w": w}
        if start is not None:
            ld["start"] = start
        if end is not None:
            ld["end"] = end
        loads.append(ld)

    for m in udl_matches2:
        w = float(m.group(1))
        # Check it's not already captured
        if not any(ld["type"] == "udl" and ld["w"] == w for ld in loads):
            loads.append({"type": "udl", "w": w})

    return loads


def _extract_per_span_loads(text, n_spans):
    """
    Extract per-span load definitions for continuous beams.
    Patterns like: "span AB has UDL 20kN/m", "span BC carries point load 30kN at 2m"

    Returns: list of lists, one per span. Each inner list contains load dicts.
             Returns None if no per-span definitions found.
    """
    span_labels = []
    for i in range(n_spans):
        left = chr(65 + i)
        right = chr(65 + i + 1)
        span_labels.append(f"{left}{right}")

    per_span = [[] for _ in range(n_spans)]
    found_any = False

    for idx, label in enumerate(span_labels):
        # Pattern: "span AB [has/carries/with] UDL 20kN/m [and point load 30kN at 2m]"
        span_pattern = re.compile(
            r'span\s+' + label + r'\s+(?:has|carries|with|:)?\s*(.*?)(?=span\s+[A-Z]{2}|$)',
            re.IGNORECASE | re.DOTALL
        )
        span_match = span_pattern.search(text)
        if not span_match:
            continue

        span_text = span_match.group(1)

        # Extract UDLs from this span's text
        udl_m = re.search(r'(?:udl|uniformly)\s*(?:of\s*)?(\d+\.?\d*)\s*kN/?m', span_text, re.IGNORECASE)
        if not udl_m:
            udl_m = re.search(r'(\d+\.?\d*)\s*kN/m', span_text, re.IGNORECASE)

        if udl_m:
            per_span[idx].append({"type": "udl", "w": float(udl_m.group(1))})
            found_any = True

        # Extract point loads from this span's text
        for pl_m in re.finditer(
            r'point\s+loads?\s*(?:of\s*)?(\d+\.?\d*)\s*kN\s*(?:at\s+(\d+\.?\d*)\s*m)?',
            span_text, re.IGNORECASE
        ):
            P = float(pl_m.group(1))
            a = float(pl_m.group(2)) if pl_m.group(2) else None
            per_span[idx].append({"type": "point_load", "P": P, "a": a})
            found_any = True

    return per_span if found_any else None


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
        "wall_height": params["wall_height"] if params["wall_height"] is not None else 0.0,
        "wall_thickness": params["wall_thickness"] if params["wall_thickness"] is not None else 0.0,
        "density": params["density"] if params["density"] is not None else 20.0,
        "beam_type": params.get("beam_type") or "simply_supported",
        "load_type": params.get("load_type") or "udl",
        "load_position": params.get("load_position"),
        "support_left": params.get("support_left") or "pinned",
        "support_right": params.get("support_right") or "roller",
        "overhang_length": params.get("overhang_length"),
        "spans": params.get("spans"),
        "supports": params.get("supports"),
        "loads": params.get("loads"),
        "per_span_loads": params.get("per_span_loads"),
    }


def normalize_concrete_strength(fcu):
    return fcu  # For now same, but allows future conversion


def calculate_wall_load(density, thickness, height):
    return density * thickness * height