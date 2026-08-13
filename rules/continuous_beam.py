# rules/continuous_beam.py
# Three-Moment (Clapeyron's) Theorem Solver for Continuous Beams
# Supports: any number of spans, UDL & point loads, fixed/pinned/roller ends

import numpy as np
import math


# ──────────────────────────────────────────────
#  Loading Term Calculations (6Aā/L and 6Ab̄/L)
# ──────────────────────────────────────────────

def _load_terms(load_info, L):
    """
    Calculate the Three-Moment loading terms for a single span.
    
    Returns (left_term, right_term):
        left_term  = 6·A·ā / L  (first moment about LEFT support)
        right_term = 6·A·b̄ / L  (first moment about RIGHT support)
    
    load_info: dict, or list of dicts. Each dict has:
        {"type": "udl", "w": <value>}
        {"type": "point_load", "P": <value>, "a": <distance from left>}
        {"type": "none"}  (no load on this span)
    
    If load_info is a list, loading terms are summed (superposition).
    """
    # Handle list of loads (multiple loads per span)
    if isinstance(load_info, list):
        total_left = 0.0
        total_right = 0.0
        for single_load in load_info:
            lt, rt = _load_terms_single(single_load, L)
            total_left += lt
            total_right += rt
        return total_left, total_right

    # Single load dict (backward compatible)
    return _load_terms_single(load_info, L)


def _load_terms_single(load_info, L):
    """Calculate loading terms for a single load on a span."""
    if load_info.get("type") == "udl":
        w = load_info["w"]
        # Parabolic free BMD: symmetric
        term = w * L**3 / 4
        return term, term

    elif load_info.get("type") == "point_load":
        P = load_info["P"]
        a = load_info.get("a", L / 2)  # default to midspan
        b = L - a
        left_term = P * a * (L**2 - a**2) / L
        right_term = P * b * a * (2 * L - a) / L
        return left_term, right_term

    else:
        return 0.0, 0.0


# ──────────────────────────────────────────────
#  Three-Moment Equation System Builder
# ──────────────────────────────────────────────

def solve_three_moment(spans, loads, support_types):
    """
    Solve a continuous beam using the Three-Moment Theorem.
    
    Parameters:
    -----------
    spans : list of float
        Span lengths [L1, L2, ..., Ln] (n spans)
    loads : list of dict
        Loading on each span. Each dict has:
        {"type": "udl", "w": <kN/m>}
        {"type": "point_load", "P": <kN>, "a": <m from left of span>}
        {"type": "none"}
    support_types : list of str
        Support type at each support point. Length = len(spans) + 1
        Values: "pinned", "roller", "fixed"
    
    Returns:
    --------
    dict with:
        "moments"   : list of support moments [M0, M1, ..., Mn]
        "reactions"  : list of support reactions [R0, R1, ..., Rn]
        "max_moment" : absolute maximum bending moment
        "max_shear"  : absolute maximum shear force
        "diagrams"   : list of per-span diagram data
    """
    n = len(spans)           # number of spans
    n_supports = n + 1       # number of supports (0, 1, ..., n)

    # ── Identify unknowns ──
    # Fixed supports → M is unknown
    # Pinned/roller supports → M = 0 (known)
    unknown_indices = []
    known_moments = {}

    for i in range(n_supports):
        if support_types[i] == "fixed":
            unknown_indices.append(i)
        else:
            known_moments[i] = 0.0  # pinned/roller → M = 0

    # Interior supports always have unknown moments (even if pinned at ends)
    for i in range(1, n):
        if i not in unknown_indices:
            unknown_indices.append(i)
            if i in known_moments:
                del known_moments[i]

    unknown_indices.sort()
    num_unknowns = len(unknown_indices)

    # Map: unknown index → position in solution vector
    idx_map = {idx: pos for pos, idx in enumerate(unknown_indices)}

    # ── Precompute loading terms for each span ──
    left_terms = []   # 6Aā/L for each span
    right_terms = []  # 6Ab̄/L for each span
    for i in range(n):
        lt, rt = _load_terms(loads[i], spans[i])
        left_terms.append(lt)
        right_terms.append(rt)

    # ── Build system of equations: A·x = b ──
    A_matrix = np.zeros((num_unknowns, num_unknowns))
    b_vector = np.zeros(num_unknowns)

    equation_row = 0

    # --- Equation for fixed LEFT end (support 0) ---
    if support_types[0] == "fixed" and 0 in idx_map:
        # Modified Three-Moment: imaginary span of length 0 to the left
        # 2·M0·L1 + M1·L1 = -6·(right_term for span 1)
        # But span indexing: span 0 has length spans[0], between support 0 and 1
        L1 = spans[0]
        row = equation_row

        # M0 coefficient
        A_matrix[row, idx_map[0]] = 2 * L1

        # M1 coefficient
        if 1 in idx_map:
            A_matrix[row, idx_map[1]] = L1
        else:
            b_vector[row] -= known_moments.get(1, 0) * L1

        # RHS
        b_vector[row] += -right_terms[0]

        equation_row += 1

    # --- Interior support equations (supports 1 to n-1) ---
    for i in range(1, n):
        # Three-Moment for supports (i-1, i, i+1):
        # M_{i-1}·L_i + 2·M_i·(L_i + L_{i+1}) + M_{i+1}·L_{i+1} = -6(Φ_i + Ψ_{i+1})
        # span i = spans[i-1] (between support i-1 and i)
        # span i+1 = spans[i] (between support i and i+1)

        L_left = spans[i - 1]   # span to the left of support i
        L_right = spans[i]      # span to the right of support i

        row = equation_row

        # M_{i-1} coefficient
        if (i - 1) in idx_map:
            A_matrix[row, idx_map[i - 1]] = L_left
        else:
            b_vector[row] -= known_moments.get(i - 1, 0) * L_left

        # M_i coefficient (center)
        if i in idx_map:
            A_matrix[row, idx_map[i]] = 2 * (L_left + L_right)

        # M_{i+1} coefficient
        if (i + 1) in idx_map:
            A_matrix[row, idx_map[i + 1]] = L_right
        else:
            b_vector[row] -= known_moments.get(i + 1, 0) * L_right

        # RHS: -6 * (left_term of right span + right_term of left span)
        # left_term of right span = 6Aā/L for spans[i] (about support i)
        # right_term of left span = 6Ab̄/L for spans[i-1] (about support i)
        # Wait: need to be careful about which term goes where.
        # For support i:
        #   From span to the LEFT (spans[i-1]): use the RIGHT term (6Ab̄/L)
        #   From span to the RIGHT (spans[i]): use the LEFT term (6Aā/L)
        rhs = -(right_terms[i - 1] + left_terms[i])
        b_vector[row] += rhs

        equation_row += 1

    # --- Equation for fixed RIGHT end (support n) ---
    if support_types[n] == "fixed" and n in idx_map:
        # M_{n-1}·Ln + 2·Mn·Ln = -6·(left_term for last span)
        Ln = spans[n - 1]
        row = equation_row

        # M_{n-1} coefficient
        if (n - 1) in idx_map:
            A_matrix[row, idx_map[n - 1]] = Ln
        else:
            b_vector[row] -= known_moments.get(n - 1, 0) * Ln

        # Mn coefficient
        A_matrix[row, idx_map[n]] = 2 * Ln

        # RHS
        b_vector[row] += -left_terms[n - 1]

        equation_row += 1

    # ── Solve ──
    moments_solution = np.linalg.solve(A_matrix[:equation_row, :equation_row],
                                        b_vector[:equation_row])

    # ── Assemble full moments array ──
    support_moments = [0.0] * n_supports
    for i in range(n_supports):
        if i in idx_map:
            support_moments[i] = round(float(moments_solution[idx_map[i]]), 4)
        else:
            support_moments[i] = known_moments.get(i, 0.0)

    # ── Calculate reactions using equilibrium per span ──
    reactions = _compute_reactions(spans, loads, support_moments)

    # ── Generate diagrams for each span ──
    diagrams = _generate_span_diagrams(spans, loads, support_moments, reactions)

    # ── Find max values ──
    max_moment = max(abs(m) for m in support_moments)
    max_shear = 0.0
    for d in diagrams:
        span_max_m = max(abs(v) for v in d["moment"])
        span_max_v = max(abs(v) for v in d["shear"])
        max_moment = max(max_moment, span_max_m)
        max_shear = max(max_shear, span_max_v)

    return {
        "moments": support_moments,
        "reactions": [round(r, 4) for r in reactions],
        "max_moment": round(max_moment, 4),
        "max_shear": round(max_shear, 4),
        "diagrams": diagrams,
    }


# ──────────────────────────────────────────────
#  Reaction Computation (per span equilibrium)
# ──────────────────────────────────────────────

def _compute_reactions(spans, loads, moments):
    """
    Compute support reactions using equilibrium on each span.
    
    For span i (between support i and i+1) with length L:
        ΣM about right = 0:  R_left * L + M_left - M_right - load_moment_about_right = 0
        ΣM about left  = 0:  R_right * L + M_right - M_left - load_moment_about_left = 0
    
    Note: moments are signed (negative = hogging at support).
    """
    n = len(spans)
    reactions = [0.0] * (n + 1)

    for i in range(n):
        L = spans[i]
        M_left = moments[i]
        M_right = moments[i + 1]
        load = loads[i]

        # Load moment about left and right supports (for free beam)
        load_list = loads[i]
        if not isinstance(load_list, list):
            load_list = [load_list]

        load_moment_about_right = 0.0
        load_moment_about_left = 0.0

        for ld in load_list:
            if ld.get("type") == "udl":
                w = ld["w"]
                load_moment_about_right += w * L**2 / 2
                load_moment_about_left += w * L**2 / 2
            elif ld.get("type") == "point_load":
                P = ld["P"]
                a = ld.get("a", L / 2)
                b = L - a
                load_moment_about_right += P * b
                load_moment_about_left += P * a

        # ΣM_right = 0: R_left·L = load_moment_about_right + M_right - M_left
        R_left = (load_moment_about_right + M_right - M_left) / L

        # ΣM_left = 0: R_right·L = load_moment_about_left + M_left - M_right
        R_right = (load_moment_about_left + M_left - M_right) / L

        reactions[i] += R_left
        reactions[i + 1] += R_right

    return reactions


# ──────────────────────────────────────────────
#  Per-Span Diagram Generation
# ──────────────────────────────────────────────

def _generate_span_diagrams(spans, loads, moments, reactions):
    """
    Generate SFD and BMD data for each span.
    Returns list of dicts, one per span.
    """
    diagrams = []
    cumulative_x = 0.0  # running x position from beam start

    for i in range(len(spans)):
        L = spans[i]
        M_left = moments[i]
        R_left_total = reactions[i]

        # For the leftmost span, R_left = reactions[0]
        # For subsequent spans, we need the shear just after the support
        # V just after support i = sum of all reactions from 0 to i minus loads on previous spans

        load = loads[i]
        steps = 30
        dx = L / steps

        x_vals = []
        shear_vals = []
        moment_vals = []
        load_vals = []

        # Calculate V and M at start of this span (just after support i)
        V_start = _shear_at_support(i, spans, loads, reactions)

        for j in range(steps + 1):
            x_local = round(j * dx, 6)
            x_global = round(cumulative_x + x_local, 4)

            # Shear and moment at x_local from left support of this span
            V, M = _compute_vm_at_x(x_local, L, load, V_start, M_left)

            load_val = 0.0
            load_list = load if isinstance(load, list) else [load]
            for ld in load_list:
                if ld.get("type") == "udl":
                    load_val += ld["w"]

            x_vals.append(x_global)
            shear_vals.append(round(V, 4))
            moment_vals.append(round(M, 4))
            load_vals.append(round(load_val, 4))

        diagrams.append({
            "span_index": i,
            "span_length": L,
            "x": x_vals,
            "shear": shear_vals,
            "moment": moment_vals,
            "load": load_vals,
            "M_left": round(M_left, 4),
            "M_right": round(moments[i + 1], 4),
        })

        cumulative_x += L

    return diagrams


def _shear_at_support(support_idx, spans, loads, reactions):
    """
    Calculate shear force just to the right of a support.
    V = sum of reactions at supports 0..support_idx minus all loads on spans 0..support_idx-1
    """
    V = 0.0
    for k in range(support_idx + 1):
        V += reactions[k]

    # Subtract loads from previous spans
    for k in range(support_idx):
        L = spans[k]
        load_list = loads[k]
        if not isinstance(load_list, list):
            load_list = [load_list]
        for ld in load_list:
            if ld.get("type") == "udl":
                V -= ld["w"] * L
            elif ld.get("type") == "point_load":
                V -= ld["P"]

    return V


def _compute_vm_at_x(x, L, loads, V_start, M_left):
    """
    Compute V and M at distance x from the left support of a single span.
    V_start: shear just after the left support
    M_left: moment at the left support
    """
    load_list = loads if isinstance(loads, list) else [loads]
    V_load_drop = 0.0
    M_load_drop = 0.0

    for ld in load_list:
        if ld.get("type") == "udl":
            w = ld["w"]
            V_load_drop += w * x
            M_load_drop += w * x**2 / 2
        elif ld.get("type") == "point_load":
            P = ld["P"]
            a = ld.get("a", L / 2)
            if x >= a:
                V_load_drop += P
                M_load_drop += P * (x - a)

    V = V_start - V_load_drop
    M = M_left + V_start * x - M_load_drop

    return V, M


# ──────────────────────────────────────────────
#  Merged Diagram Output (all spans combined)
# ──────────────────────────────────────────────

def merge_diagrams(diagrams):
    """
    Merge per-span diagrams into single arrays for plotting.
    Returns (x_vals, shear_vals, moment_vals, load_vals)
    """
    x_all, shear_all, moment_all, load_all = [], [], [], []

    for i, d in enumerate(diagrams):
        start = 1 if i > 0 else 0  # skip first point of subsequent spans (avoid duplicates)
        x_all.extend(d["x"][start:])
        shear_all.extend(d["shear"][start:])
        moment_all.extend(d["moment"][start:])
        load_all.extend(d["load"][start:])

    return x_all, shear_all, moment_all, load_all
