from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
import base64
import io
import os
import tempfile
from PIL import Image as PILImage


def generate_pdf(data, filename="beam_report.pdf"):
    """
    Generate a comprehensive PDF report from the full design data.
    Handles single-span and continuous beams, including:
    - Input parameters
    - Load breakdown
    - Bending design (BS 8110)
    - Deflection check (Table 3.9)
    - Shear reinforcement design
    - Continuous beam analysis (if applicable)
    """
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm,
                            leftMargin=15*mm, rightMargin=15*mm)
    styles = getSampleStyleSheet()

    # Custom styles
    heading2 = ParagraphStyle('Heading2Custom', parent=styles["Heading2"],
                               spaceAfter=6, spaceBefore=12,
                               textColor=colors.HexColor("#1e3a5f"))
    label_style = ParagraphStyle('Label', parent=styles["Normal"],
                                  fontSize=10, spaceAfter=2)
    value_style = ParagraphStyle('Value', parent=styles["Normal"],
                                  fontSize=10, spaceAfter=4, fontName="Helvetica-Bold")

    content = []

    # ══════════════════════════════════════════
    #  TITLE
    # ══════════════════════════════════════════
    content.append(Paragraph("AI-RCBDS: Reinforced Concrete Beam Design System<br/>Results Report", styles["Title"]))
    content.append(Spacer(1, 6))

    # ══════════════════════════════════════════
    #  1. INPUT PARAMETERS
    # ══════════════════════════════════════════
    inp = data.get("input", {})
    content.append(Paragraph("1. Input Parameters", heading2))

    beam_type_labels = {
        "simply_supported": "Simply Supported",
        "cantilever": "Cantilever",
        "continuous": "Continuous",
        "overhang": "Overhang"
    }
    load_type_labels = {
        "udl": "UDL (Uniformly Distributed)",
        "point_load": "Point Load",
        "triangular": "Triangular"
    }

    bt = beam_type_labels.get(inp.get("beam_type", ""), inp.get("beam_type", "N/A"))
    lt = load_type_labels.get(inp.get("load_type", ""), inp.get("load_type", "N/A"))

    # Span display — multi-span for continuous, single for others
    if data.get("continuous"):
        spans = data["continuous"].get("spans", [])
        span_str = " + ".join([f"{s}m" for s in spans]) + f"  ({len(spans)}-span)"
    else:
        span_str = f"{inp.get('span', 'N/A')} m"

    input_data = [
        ["Beam Type", bt],
        ["Load Type", lt],
        ["Span", span_str],
        ["Load", f"{inp.get('load', 'N/A')} {'kN' if inp.get('load_type') == 'point_load' else 'kN/m'}"],
        ["Concrete (fcu)", f"{inp.get('fcu') or inp.get('fck', 'N/A')} N/mm²"],
        ["Steel (fy)", f"{inp.get('fy', 'N/A')} N/mm²"],
    ]

    # Add overhang length for overhang beams
    oh_len = inp.get("overhang_length", 0) or 0
    if inp.get("beam_type") == "overhang" and oh_len > 0:
        input_data.insert(3, ["Overhang Length", f"{oh_len} m"])

    # Supports
    if data.get("continuous"):
        supports = data["continuous"].get("supports", [])
        sup_str = " → ".join([s.title() for s in supports])
        input_data.append(["Supports", sup_str])
    else:
        sl = (inp.get("support_left") or "pinned").title()
        sr = (inp.get("support_right") or "roller").title()
        input_data.append(["Supports", f"{sl} — {sr}"])

    _add_table(content, input_data)

    # ══════════════════════════════════════════
    #  2. BEAM SIZE
    # ══════════════════════════════════════════
    beam = data.get("beam", {})
    content.append(Paragraph("2. Beam Size", heading2))
    size_str = f"{beam.get('width', 'N/A')}mm × {beam.get('depth', 'N/A')}mm"
    if beam.get("resized"):
        size_str += "  (RESIZED)"
    content.append(Paragraph(size_str, value_style))

    # ══════════════════════════════════════════
    #  3. LOAD BREAKDOWN
    # ══════════════════════════════════════════
    res = data.get("results", {})
    content.append(Paragraph("3. Load Breakdown", heading2))

    load_data = [
        ["n1 — Slab Load", f"{res.get('n1_slab_load', 0)} kN/m"],
        ["n2 — Beam Self-Weight", f"{res.get('n2_beam_self_weight', 0)} kN/m"],
    ]

    wall_uw = res.get("wall_unit_weight", 0)
    wall_th = res.get("wall_thickness", 0)
    wall_ht = res.get("wall_height", 0)
    wall_ll = res.get("wall_line_load", 0)
    has_wall = wall_ht > 0 and wall_th > 0

    if has_wall:
        load_data.append(["Wall Unit Weight", f"{wall_uw} kN/m³"])
        load_data.append(["Wall Thickness", f"{wall_th} m"])
        load_data.append(["Wall Height", f"{wall_ht} m"])
        load_data.append(["Wall Line Load", f"{wall_ll} kN/m"])
        load_data.append(["n3 — Factored Wall Load", f"{res.get('n3_wall_load', 0)} kN/m"])
    else:
        load_data.append(["n3 — Factored Wall Load", "0 kN/m (no wall)"])

    load_data.append(["w — Total UDL", f"{res.get('w_total_udl', 0)} kN/m"])
    load_data.append(["p1 — Point Load", f"{res.get('p1_point_load', 0)} kN"])
    
    # Show multi-load combinations if present
    inp = data.get("input", {})
    if inp.get("per_span_loads"):
        for i, span_loads in enumerate(inp["per_span_loads"]):
            label_L = chr(65 + i)
            label_R = chr(66 + i)
            desc_list = []
            for ld in span_loads:
                if ld.get("type") == "udl": desc_list.append(f"UDL {ld.get('w')}kN/m")
                elif ld.get("type") == "point_load": desc_list.append(f"PL {ld.get('P')}kN at {ld.get('a')}m")
            load_data.append([f"Span {label_L}{label_R} Loads", " + ".join(desc_list)])
    elif inp.get("loads"):
        desc_list = []
        for ld in inp["loads"]:
            if ld.get("type") == "udl":
                if ld.get("start") is not None and ld.get("end") is not None:
                    desc_list.append(f"Partial UDL {ld.get('w')}kN/m ({ld.get('start')}m–{ld.get('end')}m)")
                else:
                    desc_list.append(f"UDL {ld.get('w')}kN/m")
            elif ld.get("type") == "point_load":
                desc_list.append(f"PL {ld.get('P')}kN at {ld.get('a')}m")
        load_data.append(["Combined Loads", " + ".join(desc_list)])

    _add_table(content, load_data)

    # Engineering note
    if has_wall:
        wall_note = (f"Wall Line Load = Unit Weight × Thickness × Height "
                     f"= {wall_uw} × {wall_th} × {wall_ht} = {wall_ll} kN/m. "
                     f"n3 = 1.4 × {wall_ll} = {res.get('n3_wall_load', 0)} kN/m.")
    else:
        wall_note = "No wall dimensions supplied — wall load (n3) = 0."
    content.append(Paragraph(wall_note, ParagraphStyle(
        "WallNote", fontSize=7, textColor=colors.grey, spaceAfter=4)))

    # ══════════════════════════════════════════
    #  4. DESIGN RESULTS
    # ══════════════════════════════════════════
    content.append(Paragraph("4. Design Results", heading2))

    design_data = [
        ["M (UDL)", f"{res.get('M_udl', 'N/A')} kNm"],
        ["M (Point)", f"{res.get('M_point', 'N/A')} kNm"],
        ["M (Total)", f"{res.get('bending_moment', 'N/A')} kNm"],
        ["Max Shear Force", f"{res.get('max_shear_force', 'N/A')} kN"],
        ["As required", f"{res.get('steel_area', 'N/A')} mm²"],
    ]

    reinf = data.get("reinforcement", {})
    design_data.append(["As provided", f"{reinf.get('provided_area', 'N/A')} mm²"])
    design_data.append(["Reinforcement", reinf.get("recommended", "N/A")])

    _add_table(content, design_data)

    # ══════════════════════════════════════════
    #  5. BS 8110 BENDING DESIGN
    # ══════════════════════════════════════════
    des = data.get("design", {})
    if des:
        content.append(Paragraph("5. BS 8110 Bending Design", heading2))

        bending_data = [
            ["Mu (Moment of Resistance)", f"{des.get('Mu', 'N/A')} kNm"],
            ["d (Effective Depth)", f"{des.get('d', 'N/A')} mm"],
            ["K = M/(fcu·b·d²)", str(des.get("K", "N/A"))],
            ["K used", str(des.get("K_used", "N/A"))],
            ["z (Lever Arm)", f"{des.get('z', 'N/A')} mm"],
            ["Status", des.get("message", "N/A")],
        ]
        _add_table(content, bending_data)

    # ══════════════════════════════════════════
    #  6. DEFLECTION CHECK (TABLE 3.9)
    # ══════════════════════════════════════════
    defl = data.get("deflection", {})
    if isinstance(defl, dict) and defl.get("status"):
        content.append(Paragraph("6. BS 8110 Deflection Check", heading2))

        defl_data = [
            ["Basic span/d ratio", str(defl.get("basic_ratio", "N/A"))],
            ["Service Stress (fs)", f"{defl.get('fs', 'N/A')} N/mm²"],
            ["Modification Factor (MF)", str(defl.get("MF", "N/A"))],
            ["Allowable span/d", str(defl.get("allowable_ratio", "N/A"))],
            ["Actual span/d", str(defl.get("actual_ratio", "N/A"))],
            ["Status", defl.get("message", "N/A")],
        ]
        if defl.get("fixed"):
            defl_data.append(["Note", "Reinforcement/depth adjusted to satisfy deflection"])
        _add_table(content, defl_data)

    # ══════════════════════════════════════════
    #  7. SHEAR REINFORCEMENT DESIGN
    # ══════════════════════════════════════════
    sd = data.get("shear_design", {})
    if sd:
        content.append(Paragraph("7. BS 8110 Shear Reinforcement Design", heading2))

        shear_data = [
            ["Ultimate Shear (V)", f"{sd.get('V_kN', 'N/A')} kN"],
            ["Shear Stress (v)", f"{sd.get('v', 'N/A')} N/mm²"],
            ["Ultimate Limit (vmax)", f"{sd.get('v_max', 'N/A')} N/mm²"],
            ["Concrete Capacity (vc)", f"{sd.get('vc', 'N/A')} N/mm²"],
            ["Link Type", sd.get("link_type", "N/A").title()],
            ["Stirrups", sd.get("link_description", "N/A")],
            ["Status", sd.get("message", "N/A")],
        ]
        _add_table(content, shear_data)

    # ══════════════════════════════════════════
    #  8. CONTINUOUS BEAM ANALYSIS
    # ══════════════════════════════════════════
    cont = data.get("continuous")
    if cont:
        content.append(Paragraph("8. Continuous Beam Analysis (Three-Moment Theorem)", heading2))

        spans = cont.get("spans", [])
        content.append(Paragraph(
            f"Spans: {' + '.join([str(s) + 'm' for s in spans])}  ({cont.get('n_spans', len(spans))}-span beam)",
            label_style))
        content.append(Spacer(1, 4))

        # Support moments
        moments = cont.get("support_moments", [])
        if moments:
            mom_rows = [["Support", "Moment (kNm)"]]
            for i, m in enumerate(moments):
                label = chr(65 + i)
                mom_rows.append([f"M{label}", f"{m:.2f}"])
            _add_table(content, mom_rows, header=True)

        # Reactions
        reactions = cont.get("reactions", [])
        if reactions:
            react_rows = [["Support", "Reaction (kN)"]]
            for i, r in enumerate(reactions):
                label = chr(65 + i)
                react_rows.append([f"R{label}", f"{r:.2f}"])
            _add_table(content, react_rows, header=True)

        # Per-location reinforcement table
        sup_designs = cont.get("support_designs", [])
        span_designs = cont.get("span_designs", [])
        all_designs = []
        if sup_designs:
            all_designs += [d for d in sup_designs if d.get("As_req", 0) > 0]
        if span_designs:
            all_designs += span_designs

        if all_designs:
            content.append(Spacer(1, 4))
            content.append(Paragraph("Reinforcement Design (Per Location)", heading2))
            reinf_rows = [["Location", "Type", "M (kNm)", "K", "z (mm)", "As_req (mm²)", "Reinforcement"]]
            for d in all_designs:
                reinf_rows.append([
                    d.get("location", ""),
                    d.get("type", ""),
                    f"{d.get('M', 0):.2f}",
                    f"{d.get('K', 0):.5f}",
                    f"{d.get('z', 0):.1f}",
                    f"{d.get('As_req', 0):.1f}",
                    d.get("reinforcement", "N/A"),
                ])
            _add_table(content, reinf_rows, header=True)

    # ══════════════════════════════════════════
    #  9. DIAGRAMS (from frontend canvases)
    # ══════════════════════════════════════════
    diagrams_b64 = data.get("diagrams_base64", {})
    diagram_labels = [
        ("beam_diagram", "Beam Diagram"),
        ("load_diagram", "Load Diagram"),
        ("shear_diagram", "Shear Force Diagram"),
        ("moment_diagram", "Bending Moment Diagram"),
    ]

    has_diagrams = any(diagrams_b64.get(k) for k, _ in diagram_labels)
    if has_diagrams:
        content.append(Paragraph("9. Diagrams", heading2))

        for key, title in diagram_labels:
            b64_str = diagrams_b64.get(key)
            if not b64_str:
                continue

            # Strip the data URL prefix ("data:image/png;base64,...")
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]

            try:
                img_bytes = base64.b64decode(b64_str)
                img_buf = io.BytesIO(img_bytes)

                # Read actual image dimensions to preserve aspect ratio
                from reportlab.lib.utils import ImageReader

                # For Chart.js graphs, add dark background so white text is visible
                # (beam_diagram already has its own drawn background)
                if key != "beam_diagram":
                    pil_img = PILImage.open(img_buf).convert("RGBA")
                    bg = PILImage.new("RGBA", pil_img.size, (30, 41, 59, 255))  # #1e293b
                    bg.paste(pil_img, (0, 0), pil_img)  # composite with alpha
                    img_buf = io.BytesIO()
                    bg.convert("RGB").save(img_buf, format="PNG")
                    img_buf.seek(0)

                ir = ImageReader(img_buf)
                iw, ih = ir.getSize()  # pixel dimensions
                img_buf.seek(0)  # reset buffer after reading

                # Scale to fit page width, preserving aspect ratio
                page_w = A4[0] - 30 * mm  # available width
                scale = page_w / iw
                img_h = ih * scale

                # Cap chart diagram height so all 3 fit on one A4 page
                # (~730pt usable height / 3 charts ≈ 195pt each after titles+spacing)
                if key != "beam_diagram":
                    max_chart_h = 195
                    if img_h > max_chart_h:
                        img_h = max_chart_h
                        page_w = iw * (max_chart_h / ih)

                img = Image(img_buf, width=page_w, height=img_h)
                img.hAlign = "CENTER"

                content.append(Paragraph(title, label_style))
                content.append(Spacer(1, 4))
                content.append(img)
                content.append(Spacer(1, 14))
            except Exception:
                pass  # Skip if image decode fails

    # ══════════════════════════════════════════
    #  FOOTER
    # ══════════════════════════════════════════
    content.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles["Normal"],
                                   fontSize=8, textColor=colors.grey, alignment=1)
    content.append(Paragraph(
       "Generated by AI Reinforced Concrete Beam Design System (Software) — A Final Year Project © 2026",   # "— MEEK Technology © 2026"
        footer_style))

    doc.build(content)
    return filename


def _add_table(content, rows, header=False):
    """Helper to add a styled 2-column table."""
    col_count = len(rows[0]) if rows else 2

    t = Table(rows, hAlign="LEFT")
    style_cmds = [
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]

    if header:
        style_cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8ecf1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#cccccc")),
        ]

    t.setStyle(TableStyle(style_cmds))
    content.append(t)
    content.append(Spacer(1, 6))