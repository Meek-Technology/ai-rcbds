"""Test all prompt examples from test_additions.md against the parser."""
import sys, json
sys.path.insert(0, ".")
from nlp.prompt_parser import extract_parameters, apply_defaults

prompts = [
    # 1. Simply Supported — Point Load + UDL
    "Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m",
    # 2. Simply Supported — Multiple Point Loads
    "Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m",
    # 3. Simply Supported — Partial UDL + Point Load
    "Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m",
    # 4. Overhang — UDL + Point Load at Free End
    "Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end",
    # 5. Overhang — Multiple Point Loads
    "Overhang beam 5m span, 1.5m overhang, point loads 20kN at 3m and 15kN at 6.5m",
    # 6. Continuous — Mixed loads across 3 spans
    "3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m",
    # 7. Continuous — 2-span with mixed loads
    "Continuous beam spans 4m and 5m, UDL 18kN/m on first span, point load 35kN at 2.5m on second span",
    # 8. Cantilever — UDL + Point Load
    "Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m",
    # 9. Basic simply supported UDL (backward compat)
    "Design a simply supported beam with span 6m, UDL of 25kN/m, fcu 30 and fy 500",
]

for i, p in enumerate(prompts, 1):
    print(f"\n{'='*70}")
    print(f"PROMPT {i}: {p}")
    print(f"{'='*70}")
    try:
        result = extract_parameters(p)
        # Show key fields
        print(f"  beam_type    : {result['beam_type']}")
        print(f"  load_type    : {result['load_type']}")
        print(f"  span         : {result['span']}")
        print(f"  load (legacy): {result['load']}")
        print(f"  point_load   : {result['point_load']}")
        print(f"  overhang     : {result['overhang_length']}")
        print(f"  spans        : {result['spans']}")
        print(f"  loads        : {json.dumps(result['loads'], indent=2) if result['loads'] else 'None'}")
        print(f"  per_span_loads: {json.dumps(result['per_span_loads'], indent=2) if result.get('per_span_loads') else 'None'}")
        
        # Test apply_defaults
        defaults = apply_defaults(result)
        print(f"  [PASS] apply_defaults passed")
    except Exception as e:
        print(f"  [FAIL] ERROR: {e}")
