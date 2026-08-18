import re


def extract_parameters(text):
    # ── Span (e.g., "6m" or "span 6m") ──
    span_match = re.search(r'span\s*(?:of\s*)?(\d+\.?\d*)\s*m', text, re.IGNORECASE) or \
                 re.search(r'(\d+\.?\d*)\s*m\b(?!\s*(?:Pa|pa|height|thick))', text)

    # ── Multiple spans (e.g., "spans 6m, 5m, 4m" or "spans 6m 5m 4m") ──
    # ── Multiple spans (e.g., "spans 6m, 5m, 4m" or "spans 4m and 5m") ──
    multi_span_match = re.search(
        r'spans?\s+(?:of\s+)?((?:\d+\.?\d*\s*m?(?:[\s,]+(?:and\s+)?|\s+)){2,5})',
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

    # ── Self-weight override (e.g., "ignore beam self weight", "ignore self weight", "without self weight") ──
    ignore_sw_pattern = r'\b(?:ignore|without|no|exclude)\s+(?:beam\s+)?self[\s-]*weight\b'
    ignore_self_weight = bool(re.search(ignore_sw_pattern, text, re.IGNORECASE))

    # ── Beam type ──
    beam_type_match = re.search(
        r'(simply\s+supported|cantilever|continuous|overhang(?:ing)?)',
        text, re.IGNORECASE
    )

    # ── Overhang length (e.g., "overhang 2m", "overhang of 2m", "1.5m overhang", "overhang BC of 2m") ──
    # Handle "Xm overhang" (e.g., "1.5m overhang", but not "span 6m overhang")
    num_before_overhang = re.search(r'(?<!span\s)(?<!span\s\s)\b(\d+\.?\d*)\s*m\s+overhang\b', text, re.IGNORECASE)
    if num_before_overhang:
        overhang_len_val = float(num_before_overhang.group(1))
    else:
        overhang_len_val = None
        # Look for explicit "overhang [length/of/BC/etc] Xm" where "span" is not in between
        for om in re.finditer(r'overhang[^\d\n]*?(\d+\.?\d*)\s*m\b', text, re.IGNORECASE):
            snippet = om.group(0).lower()
            if "span" not in snippet and "beam" not in snippet:
                overhang_len_val = float(om.group(1))
                break

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

    # ── Legacy single-load values and multi-point load extraction ──
    load_value = None
    point_load_value = 0
    load_pos = None

    # First: find UDL intensity for `load_value`
    udl_loads = [ld for ld in loads_list if ld["type"] == "udl"]
    if udl_loads:
        load_value = udl_loads[0]["w"]

    # Second: extract point loads array
    point_loads = [ld for ld in loads_list if ld["type"] == "point_load"]
    if point_loads:
        point_load_value = point_loads[0]["P"]
        load_pos = point_loads[0].get("a")

    # If NO UDL was found, load_value is 0.0 for legacy fallback
    if load_value is None:
        load_value = 0.0

    # Build p1, p2, p3... and a1, a2, a3... fields for multiple point loads
    p_dict = {}
    for idx, pl in enumerate(point_loads, 1):
        p_dict[f"p{idx}"] = pl["P"]
        p_dict[f"a{idx}"] = pl.get("a")

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
    overhang_len = overhang_len_val
    span_val = float(span_match.group(1)) if span_match else None

    # If an overhang length is detected, it's an overhang beam
    if overhang_len is not None:
        beam_type = "overhang"

    # "free end" detection: if load is at the free end of an overhang,
    # load_position = span + overhang_length
    free_end_match = re.search(r'free\s+end', text, re.IGNORECASE)
    if beam_type == "overhang" and free_end_match and overhang_len and span_val:
        load_pos = span_val + overhang_len

    # ── Multi-span extraction (for continuous beams) ──
    spans_list = None
    supports_list = None

    # ── Multi-span extraction (for continuous beams) ──
    spans_list = None
    supports_list = None

    # Pattern A: "Span AB = 12 m, BC = 12 m, and CD = 4 m" or "span AB is 3 m and span BC is 4 m"
    raw_ab = re.findall(r'([A-Z]{2})\s*[:=is]*\s*(\d+\.?\d*)\s*m', text, re.IGNORECASE)
    valid_ab = []
    for label, val in raw_ab:
        lbl = label.upper()
        # Verify it's a valid sequential span label like AB, BC, CD, DE...
        if len(lbl) == 2 and ord(lbl[1]) == ord(lbl[0]) + 1:
            valid_ab.append((lbl, float(val)))

    if valid_ab:
        # Preserve sequence order by sorting on span label (AB, BC, CD...)
        valid_ab.sort(key=lambda x: x[0])
        spans_list = [v for lbl, v in valid_ab]
        beam_type = "continuous"
        if not span_val:
            span_val = spans_list[0]

    # Pattern B: "spans 6m, 5m, 4m" or "spans 4m and 5m"
    if not spans_list and multi_span_match:
        span_str = multi_span_match.group(1)
        spans_list = [float(v) for v in re.findall(r'\d+\.?\d*', span_str)]
        if spans_list:
            beam_type = "continuous"
            if not span_val:
                span_val = spans_list[0]

    # If continuous but only single span, replicate based on n_span_match
    if beam_type == "continuous" and not spans_list and span_val:
        n_spans = int(n_span_match.group(1)) if n_span_match else 2
        spans_list = [span_val] * n_spans

    # ── Multi-support extraction ──
    if multi_support_match:
        raw_supports = re.findall(r'(pinned|roller|fixed)', multi_support_match.group(1), re.IGNORECASE)
        supports_list = [s.lower() for s in raw_supports]

    # Node-by-node support extraction for continuous beams (e.g., "Support A and D are fixed, while B and C are roller supports")
    if beam_type == "continuous" and spans_list:
        n_supports = len(spans_list) + 1
        if not supports_list:
            supports_list = ["pinned"] * n_supports

        # Multi node pattern: "Support A and D are fixed", "B and C are roller supports"
        for m in re.finditer(r'(?:supports?\s+)?\b([A-Z])\b\s+(?:and|,)\s+\b([A-Z])\b\s+(?:are\s+)?(?:a\s+)?(fixed|roller|pinned)', text, re.IGNORECASE):
            node1 = ord(m.group(1).upper()) - 65
            node2 = ord(m.group(2).upper()) - 65
            sup_type = m.group(3).lower()
            if 0 <= node1 < n_supports:
                supports_list[node1] = sup_type
            if 0 <= node2 < n_supports:
                supports_list[node2] = sup_type

        # Single node pattern: "Support A is fixed", "Support A fixed", "B is roller"
        for m in re.finditer(r'(?:support\s+)?\b([A-Z])\b\s+(?:is\s+)?(?:a\s+)?(fixed|roller|pinned)', text, re.IGNORECASE):
            node_char = m.group(1).upper()
            sup_type = m.group(2).lower()
            node_idx = ord(node_char) - 65
            if 0 <= node_idx < n_supports:
                supports_list[node_idx] = sup_type

        # Update support_left and support_right
        support_left = supports_list[0]
        support_right = supports_list[-1]

    # ── Per-span loads for continuous beams ──
    per_span_loads = None
    if beam_type == "continuous" and spans_list:
        per_span_loads = _extract_per_span_loads(text, spans_list)

    res = {
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
        "point_loads": point_loads if point_loads else None,
        "ignore_self_weight": ignore_self_weight,
    }
    # Merge p1, p2, p3... and a1, a2, a3...
    res.update(p_dict)
    return res


def _extract_loads(text):
    """
    Extract multiple load definitions from a prompt.
    Returns a list of load dicts: [{"type": "udl", "w": ...}, {"type": "point_load", "P": ..., "a": ...}]
    """
    loads = []

    # ── Extract all point loads with positions ──
    # Patterns: "point load 30kN at 2m", "p1 = 25kN at 2m", "30kN point load at 2m"
    # Also: "point loads 25kN at 2m and 40kN at 6m"
    pl_patterns = [
        # "p1 [of] 30kN at 2m" or "P1 = 30kN at 2m"
        r'\bp\d+\s*=?\s*(\d+\.?\d*)\s*kN\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)?',
        # "point load [of] 30kN at 2m"
        r'point\s+loads?\s*(?:of\s*)?(\d+\.?\d*)\s*kN\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)?',
        # "30kN point load at 2m"
        r'(\d+\.?\d*)\s*kN\s*(?:point\s+load)\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)?',
        # "and 40kN at 6m" (secondary point loads joined by 'and')
        r'and\s+(\d+\.?\d*)\s*kN\s*(?:at\s+(?:distance\s+)?(\d+\.?\d*)\s*m)',
    ]

    # Find all point load matches
    for pat in pl_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            P = float(m.group(1))
            a = float(m.group(2)) if m.group(2) else None
            loads.append({"type": "point_load", "P": P, "a": a})

    # If "point load" appears in text, also catch standalone "XkN at Ym" patterns
    if re.search(r'point\s+load', text, re.IGNORECASE):
        for m in re.finditer(r'(\d+\.?\d*)\s*kN\s+at\s+(\d+\.?\d*)\s*m', text, re.IGNORECASE):
            P = float(m.group(1))
            a = float(m.group(2))
            # Only add if not already captured
            if not any(ld["P"] == P and ld.get("a") == a for ld in loads):
                loads.append({"type": "point_load", "P": P, "a": a})

    # Deduplicate point loads (same P and a values)
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


def _extract_per_span_loads(text, spans_or_n):
    """
    Extract per-span load definitions for continuous beams.
    Accepts either a list of span lengths (spans_list) or int (n_spans).
    """
    if isinstance(spans_or_n, list):
        spans_list = spans_or_n
        n_spans = len(spans_list)
    else:
        n_spans = spans_or_n
        spans_list = [0.0] * n_spans

    span_labels = []
    cum_spans = []
    curr = 0.0
    for i in range(n_spans):
        left = chr(65 + i)
        right = chr(65 + i + 1)
        span_labels.append(f"{left}{right}")
        s_len = spans_list[i] if i < len(spans_list) else 0.0
        cum_spans.append((curr, curr + s_len))
        curr += s_len

    per_span = [[] for _ in range(n_spans)]
    found_any = False

    ordinals = ["first", "second", "third", "fourth", "fifth"]

    # Split text into clauses/phrases
    clauses = re.split(r'[,;.\n]|(?=\bwhile\b)|(?=\band\b\s+span)', text, flags=re.IGNORECASE)

    for clause in clauses:
        clause_str = clause.strip()
        if not clause_str:
            continue

        target_idx = None

        # Check explicit span labels (AB, BC, CD...)
        for idx, label in enumerate(span_labels):
            if re.search(r'\b' + label + r'\b', clause_str, re.IGNORECASE) or \
               re.search(r'span\s+' + label, clause_str, re.IGNORECASE):
                target_idx = idx
                break

        # Check ordinal references ("first span", "second span"...)
        if target_idx is None:
            for idx, ord_word in enumerate(ordinals[:n_spans]):
                if re.search(r'\b' + ord_word + r'\s+span\b', clause_str, re.IGNORECASE) or \
                   re.search(r'\bspan\s+' + str(idx + 1) + r'\b', clause_str, re.IGNORECASE):
                    target_idx = idx
                    break

        # Check coordinate range ("from 0 to 3m", "from 12m to 24m", "0 to 3m", "12m to 24m")
        if target_idx is None and any(s_len > 0 for s_len in spans_list):
            range_m = re.search(r'(?:from\s+)?(\d+\.?\d*)\s*m?\s*(?:to|-)\s*(\d+\.?\d*)\s*m', clause_str, re.IGNORECASE)
            if range_m:
                r_start = float(range_m.group(1))
                r_end = float(range_m.group(2))
                for idx, (c_start, c_end) in enumerate(cum_spans):
                    if c_end > c_start and r_start >= c_start - 0.01 and r_end <= c_end + 0.01:
                        target_idx = idx
                        break

        if target_idx is None:
            continue

        span_len = spans_list[target_idx]

        # Extract UDL
        udl_m = re.search(r'(?:udl|uniformly)\s*(?:of\s*)?(\d+\.?\d*)\s*kN/?m', clause_str, re.IGNORECASE)
        if not udl_m:
            udl_m = re.search(r'(\d+\.?\d*)\s*kN/m', clause_str, re.IGNORECASE)

        if udl_m:
            w = float(udl_m.group(1))
            per_span[target_idx].append({"type": "udl", "w": w})
            found_any = True

        # Extract Point Load
        pl_m = re.search(r'(\d+\.?\d*)\s*kN\s+(?:point\s+load)?', clause_str, re.IGNORECASE) or \
               re.search(r'point\s+loads?\s*(?:of\s*)?(\d+\.?\d*)\s*kN', clause_str, re.IGNORECASE)

        if pl_m:
            P = float(pl_m.group(1))
            if not (udl_m and float(udl_m.group(1)) == P):
                pos_m = re.search(r'at\s+(?:distance\s+)?(\d+\.?\d*)\s*m', clause_str, re.IGNORECASE)
                if pos_m:
                    a = float(pos_m.group(1))
                elif re.search(r'midpoint|midspan|center|middle', clause_str, re.IGNORECASE):
                    a = span_len / 2.0 if span_len > 0 else None
                else:
                    a = None

                per_span[target_idx].append({"type": "point_load", "P": P, "a": a})
                found_any = True

    return per_span if found_any else None


def apply_defaults(params):
    if not params.get("span"):
        raise ValueError("Span is required but was not provided or could not be parsed.")
    has_any_load = (params.get("load") is not None and params.get("load") > 0) or \
                   (params.get("point_load") is not None and params.get("point_load") > 0) or \
                   params.get("loads") or params.get("per_span_loads")
    if not has_any_load:
        raise ValueError("Load is required but was not provided or could not be parsed.")

    res = {
        "span": params["span"],
        "load": params.get("load") if params.get("load") is not None else 0.0,
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
        "point_loads": params.get("point_loads"),
        "ignore_self_weight": bool(params.get("ignore_self_weight", False)),
    }
    # Pass through p1, p2, p3... and a1, a2, a3...
    for k, v in params.items():
        if (k.startswith("p") or k.startswith("a")) and k[1:].isdigit():
            res[k] = v
    return res


def normalize_concrete_strength(fcu):
    return fcu  # For now same, but allows future conversion


def calculate_wall_load(density, thickness, height):
    return density * thickness * height