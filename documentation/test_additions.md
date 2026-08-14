# Multi-Load Structural Test Suite (`test_additions.md`)

This document contains standardized prompt examples and expected parsing verification outputs for all structural beam types and load combinations in the AI-RCBDS system.

---

## Test Scenarios & Prompts

### Test Case 1: Simply Supported Beam — Combined Load (UDL + Single Point Load)
- **Prompt**: `"Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m"`
- **Expected Parser Output**:
  - `beam_type`: `simply_supported`
  - `load_type`: `combined`
  - `span`: `6.0`
  - `load` (legacy UDL): `20.0`
  - `point_load`: `30.0`
  - `p1`: `30.0`, `a1`: `2.0`
  - `loads`: `[{"type": "point_load", "P": 30.0, "a": 2.0}, {"type": "udl", "w": 20.0}]`

---

### Test Case 2: Simply Supported Beam — Multiple Point Loads (`p1`, `p2`)
- **Prompt**: `"Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m"`
- **Expected Parser Output**:
  - `beam_type`: `simply_supported`
  - `load_type`: `point_load`
  - `span`: `8.0`
  - `load` (legacy): `0.0`
  - `point_load`: `25.0`
  - `p1`: `25.0`, `a1`: `2.0`, `p2`: `40.0`, `a2`: `6.0`
  - `loads`: `[{"type": "point_load", "P": 25.0, "a": 2.0}, {"type": "point_load", "P": 40.0, "a": 6.0}]`

---

### Test Case 3: Simply Supported Beam — Partial UDL + Point Load
- **Prompt**: `"Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m"`
- **Expected Parser Output**:
  - `beam_type`: `simply_supported`
  - `load_type`: `combined`
  - `span`: `5.0`
  - `load`: `15.0`
  - `point_load`: `20.0`
  - `p1`: `20.0`, `a1`: `4.0`
  - `loads`: `[{"type": "point_load", "P": 20.0, "a": 4.0}, {"type": "udl", "w": 15.0, "start": 0.0, "end": 3.0}]`

---

### Test Case 4: Overhang Beam — UDL + Free End Point Load
- **Prompt**: `"Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end"`
- **Expected Parser Output**:
  - `beam_type`: `overhang`
  - `load_type`: `combined`
  - `span`: `6.0`
  - `overhang_length`: `2.0`
  - `load`: `15.0`
  - `point_load`: `10.0`
  - `p1`: `10.0`, `a1`: `8.0` (span 6m + overhang 2m)

---

### Test Case 5: Overhang Beam — Multiple Point Loads
- **Prompt**: `"Overhang beam 5m span, 1.5m overhang, point loads 20kN at 3m and 15kN at 6.5m"`
- **Expected Parser Output**:
  - `beam_type`: `overhang`
  - `load_type`: `point_load`
  - `span`: `5.0`
  - `overhang_length`: `1.5`
  - `p1`: `20.0`, `a1`: `3.0`
  - `p2`: `15.0`, `a2`: `6.5`

---

### Test Case 6: Continuous Beam — 3-Span Mixed Per-Span Loads
- **Prompt**: `"3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m"`
- **Expected Parser Output**:
  - `beam_type`: `continuous`
  - `spans`: `[5.0, 6.0, 5.0]`
  - `p1`: `30.0`, `a1`: `2.0`
  - `p2`: `25.0`, `a2`: `3.0`
  - `per_span_loads`: 3 span arrays with explicit loads assigned per span.

---

## Terminal Verification Command
To run all test cases in the terminal and verify parser output:
```bash
.\venv\Scripts\python.exe test_parser_multi.py
```
