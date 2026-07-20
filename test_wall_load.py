"""Validation tests for wall loading refactoring."""
import json
import urllib.request


def test(prompt, label):
    d = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8000/predict",
        data=d,
        headers={"Content-Type": "application/json"},
    )
    r = json.loads(urllib.request.urlopen(req).read())
    res = r.get("results", {})
    print(f"--- {label} ---")
    print(f"  wall_unit_weight: {res.get('wall_unit_weight')}")
    print(f"  wall_thickness:   {res.get('wall_thickness')}")
    print(f"  wall_height:      {res.get('wall_height')}")
    print(f"  wall_line_load:   {res.get('wall_line_load')}")
    print(f"  n3_wall_load:     {res.get('n3_wall_load')}")
    print(f"  w_total_udl:      {res.get('w_total_udl')}")
    print()


# Test 1: No wall specified -> n3 = 0
test(
    "Design a simply supported beam with span 6m, UDL 20kN/m, fcu 25",
    "TEST 1: No wall -> expect n3=0, wall_line_load=0",
)

# Test 2: Wall with default density (20.0 kN/m³)
# wall_line_load = 20.0 * 0.15 * 3 = 9.0
# n3 = 1.4 * 9.0 = 12.6
test(
    "Simply supported beam span 6m, UDL 20kN/m, fcu 25, wall height 3, wall thickness 0.15",
    "TEST 2: Default density (20.0) -> expect WLL=9.0, n3=12.6",
)

# Test 3: User-specified density (18 kN/m³)
# wall_line_load = 18 * 0.15 * 3 = 8.1
# n3 = 1.4 * 8.1 = 11.34
test(
    "Simply supported beam span 6m, UDL 20kN/m, fcu 25, wall height 3, wall thickness 0.15, density 18",
    "TEST 3: User density 18 -> expect WLL=8.1, n3=11.34",
)

# Test 4: Continuous beam with wall
test(
    "A 2-span continuous beam with spans 6m, 6m, UDL 20kN/m, fcu 25, wall height 2.5, wall thickness 0.15",
    "TEST 4: Continuous + wall -> expect wall values present",
)

print("All tests completed.")
