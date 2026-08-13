# Complex Multi-Load Prompt Examples

This file documents a test suite of advanced natural language prompts designed to validate the new multi-load and partial-load processing capabilities of the AI-RCBDS system.

## 1. Simply Supported Beams with Mixed Loads

**Prompt 1 (Point Load + UDL):**
`Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m`
- **Expected Parser Output:** `beam_type: simply_supported`, `span: 6`, `loads: [{type: udl, w: 20}, {type: point_load, P: 30, a: 2}]`

**Prompt 2 (Multiple Point Loads):**
`Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m`
- **Expected Parser Output:** `span: 8`, `loads: [{type: point_load, P: 25, a: 2}, {type: point_load, P: 40, a: 6}]`

**Prompt 3 (Partial UDL + Point Load):**
`Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m`
- **Expected Parser Output:** `span: 5`, `loads: [{type: udl, w: 15, start: 0, end: 3}, {type: point_load, P: 20, a: 4}]`


## 2. Overhang Beams with Mixed Loads

**Prompt 4 (UDL + Point Load at Free End):**
`Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end`
- **Expected Parser Output:** `beam_type: overhang`, `span: 6`, `overhang_length: 2`, `loads: [{type: udl, w: 15}, {type: point_load, P: 10, a: 8}]`
- *Note: "at free end" maps to `a = 6 + 2 = 8m`.*

**Prompt 5 (Multiple Point Loads):**
`Overhang beam 5m span, 1.5m overhang, point loads 20kN at 3m and 15kN at 6.5m`
- **Expected Parser Output:** `span: 5`, `overhang_length: 1.5`, `loads: [{type: point_load, P: 20, a: 3}, {type: point_load, P: 15, a: 6.5}]`


## 3. Continuous Beams with Per-Span Load Definitions

**Prompt 6 (Mixed loads across 3 spans):**
`3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m`
- **Expected Parser Output:** `beam_type: continuous`, `spans: [5, 6, 5]`, 
  `per_span_loads: [ [{type: udl, w: 20}], [{type: udl, w: 15}, {type: point_load, P: 30, a: 2}], [{type: point_load, P: 25, a: 3}] ]`

**Prompt 7 (2-span with mixed loads):**
`Continuous beam spans 4m and 5m, UDL 18kN/m on first span, point load 35kN at 2.5m on second span`
- **Expected Parser Output:** `spans: [4, 5]`, (Parser handles this via generic regex, or defaults to uniform loading if per-span regex misses "first span", but ideal parsing is handled).


## 4. Cantilever Beams

**Prompt 8 (UDL + Point Load):**
`Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m`
- **Expected Parser Output:** `beam_type: cantilever`, `span: 3`, `loads: [{type: udl, w: 10}, {type: point_load, P: 15, a: 3}]`
