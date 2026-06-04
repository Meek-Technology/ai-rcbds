"""
Beam Design Calculation Sheet PDF Generator
============================================
Generates an Orion-style detailed calculation sheet with:
  - Header with project info, material grades, beam geometry
  - Embedded diagrams (beam, load, SFD, BMD)
  - Tabulated bending design (top/bottom edge)
  - Shear & torsion design
  - Deflection check
  - Reinforcement schedule (steel bars)

Works for all beam types: Simply Supported, Cantilever, Continuous, Overhang.
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.lib.utils import ImageReader as _ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage
import base64
import io


# ════════════════════════════════════════════
#  Colour palette
# ════════════════════════════════════════════
HEADER_BG = colors.HexColor("#1e3a5f")
HEADER_FG = colors.white
ROW_LABEL_BG = colors.HexColor("#e8ecf1")
SECTION_BG = colors.HexColor("#cdd5e0")
PASS_COLOR = colors.HexColor("#15803d")
FAIL_COLOR = colors.HexColor("#dc2626")
GRID_COLOR = colors.HexColor("#94a3b8")
LIGHT_BLUE = colors.HexColor("#dbeafe")


def generate_calc_sheet(data, filename="calc_sheet.pdf"):
    """Generate a detailed calculation sheet PDF from the full design data."""
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        topMargin=12 * mm, bottomMargin=12 * mm,
        leftMargin=10 * mm, rightMargin=10 * mm,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_s = ParagraphStyle("CalcTitle", parent=styles["Normal"],
                              fontSize=12, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, spaceAfter=2)
    sub_s = ParagraphStyle("CalcSub", parent=styles["Normal"],
                            fontSize=8, alignment=TA_CENTER, spaceAfter=0)
    section_s = ParagraphStyle("Section", parent=styles["Normal"],
                                fontSize=9, fontName="Helvetica-Bold",
                                spaceBefore=6, spaceAfter=2)
    note_s = ParagraphStyle("Note", parent=styles["Normal"],
                             fontSize=7, textColor=colors.grey, alignment=TA_CENTER)

    content = []

    # ──────────────────────────────────────
    #  Unpack data
    # ──────────────────────────────────────
    inp = data.get("input", {})
    beam = data.get("beam", {})
    des = data.get("design", {})
    res = data.get("results", {})
    defl = data.get("deflection", {})
    sd = data.get("shear_design", {})
    reinf = data.get("reinforcement", {})
    cont = data.get("continuous")

    beam_type = inp.get("beam_type", "simply_supported")
    load_type = inp.get("load_type", "udl")
    fcu = inp.get("fcu") or inp.get("fck", 25)
    fy = inp.get("fy", 460)
    b = beam.get("width", 230)
    h = beam.get("depth", 450)

    bt_labels = {
        "simply_supported": "Simply Supported",
        "cantilever": "Cantilever",
        "continuous": "Continuous",
        "overhang": "Overhang"
    }

    # ══════════════════════════════════════════
    #  1. HEADER BLOCK
    # ══════════════════════════════════════════
    header_data = [
        [
            Paragraph("<b>AI STRUCTURAL DESIGN SYSTEM</b>", _p(10, HEADER_FG, TA_LEFT)),
            Paragraph("<b>BEAM DESIGN CALCULATION SHEET</b>", _p(10, HEADER_FG, TA_CENTER)),
            Paragraph("", _p(8, HEADER_FG, TA_RIGHT)),  # Page number added via footer
        ],
        [
            Paragraph(f"Beam Type: <b>{bt_labels.get(beam_type, beam_type)}</b>", _p(8, HEADER_FG, TA_LEFT)),
            Paragraph(f"Material: C{int(fcu)}/Grade {fy} | BS 8110", _p(8, HEADER_FG, TA_CENTER)),
            Paragraph(f"Load Type: <b>{load_type.upper()}</b>", _p(8, HEADER_FG, TA_RIGHT)),
        ],
    ]

    pw = A4[0] - 20 * mm  # page width
    ht = Table(header_data, colWidths=[pw * 0.33, pw * 0.34, pw * 0.33])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    content.append(ht)
    content.append(Spacer(1, 4))

    # ══════════════════════════════════════════
    #  2. BEAM GEOMETRY & SPANS
    # ══════════════════════════════════════════
    if cont:
        spans = cont.get("spans", [])
        supports = cont.get("supports", [])
        span_str = " + ".join([f"{s}m" for s in spans])
        sup_str = " → ".join([s.title() for s in supports])
        geo_rows = [
            [_b("Beam Size"), f"{b} × {h} mm", _b("No. of Spans"), str(len(spans))],
            [_b("Spans"), span_str, _b("Total Length"), f"{sum(spans):.1f} m"],
            [_b("Supports"), sup_str, _b("Resized"), "Yes" if beam.get("resized") else "No"],
        ]
    else:
        span = inp.get("span", 0)
        sl = inp.get("support_left", "pinned").title()
        sr = inp.get("support_right", "roller").title()
        geo_rows = [
            [_b("Beam Size"), f"{b} × {h} mm", _b("Span"), f"{span} m"],
            [_b("Left Support"), sl, _b("Right Support"), sr],
            [_b("Concrete (fcu)"), f"{fcu} N/mm²", _b("Steel (fy)"), f"{fy} N/mm²"],
        ]

    geo_t = Table(geo_rows, colWidths=[pw * 0.18, pw * 0.32, pw * 0.18, pw * 0.32])
    geo_t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("BACKGROUND", (0, 0), (0, -1), ROW_LABEL_BG),
        ("BACKGROUND", (2, 0), (2, -1), ROW_LABEL_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    content.append(geo_t)
    content.append(Spacer(1, 4))

    # ══════════════════════════════════════════
    #  3. LOAD BREAKDOWN
    # ══════════════════════════════════════════
    content.append(Paragraph("LOAD BREAKDOWN (BS 8110)", section_s))
    load_rows = [
        [_b("Component"), _b("Value"), _b("Component"), _b("Value")],
        ["n1 — Slab Load", f"{res.get('n1_slab_load', 0)} kN/m",
         "n3 — Wall Load", f"{res.get('n3_wall_load', 0)} kN/m"],
        ["n2 — Self-Weight", f"{res.get('n2_beam_self_weight', 0)} kN/m",
         "p1 — Point Load", f"{res.get('p1_point_load', 0)} kN"],
        ["w — Total UDL", f"{res.get('w_total_udl', 0)} kN/m", "", ""],
    ]
    lt = Table(load_rows, colWidths=[pw * 0.22, pw * 0.28, pw * 0.22, pw * 0.28])
    lt.setStyle(_grid_style(header_row=True))
    content.append(lt)
    content.append(Spacer(1, 4))

    # ══════════════════════════════════════════
    #  4. EMBEDDED DIAGRAMS
    # ══════════════════════════════════════════
    diagrams_b64 = data.get("diagrams_base64", {})
    diagram_order = [
        ("beam_diagram", "Beam Diagram"),
        ("load_diagram", "Load Diagram"),
        ("shear_diagram", "Shear Force Diagram (kN)"),
        ("moment_diagram", "Bending Moment Diagram (kNm)"),
    ]

    has_diagrams = any(diagrams_b64.get(k) for k, _ in diagram_order)
    if has_diagrams:
        content.append(Paragraph("DIAGRAMS", section_s))

        for key, title in diagram_order:
            b64_str = diagrams_b64.get(key)
            if not b64_str:
                continue

            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]

            try:
                img_bytes = base64.b64decode(b64_str)
                img_buf = io.BytesIO(img_bytes)

                # Add dark background for Chart.js (not beam_diagram)
                if key != "beam_diagram":
                    pil_img = PILImage.open(img_buf).convert("RGBA")
                    bg = PILImage.new("RGBA", pil_img.size, (30, 41, 59, 255))
                    bg.paste(pil_img, (0, 0), pil_img)
                    img_buf = io.BytesIO()
                    bg.convert("RGB").save(img_buf, format="PNG")
                    img_buf.seek(0)

                from reportlab.lib.utils import ImageReader
                ir = ImageReader(img_buf)
                iw, ih = ir.getSize()
                img_buf.seek(0)

                scale = pw / iw
                img_h = ih * scale
                # Cap height: beam diagram smaller, chart diagrams larger
                max_h = 100 if key == "beam_diagram" else 185
                if img_h > max_h:
                    img_h = max_h
                    pw_img = iw * (max_h / ih)
                else:
                    pw_img = pw

                img = Image(img_buf, width=pw_img, height=img_h)
                img.hAlign = "CENTER"

                content.append(Paragraph(f"<i>{title}</i>", _p(7, colors.HexColor("#64748b"), TA_CENTER)))
                content.append(img)
                content.append(Spacer(1, 4))
            except Exception:
                pass

        content.append(PageBreak())

    # ══════════════════════════════════════════
    #  5. BENDING DESIGN TABLE
    # ══════════════════════════════════════════
    content.append(Paragraph("BENDING DESIGN (BS 8110)", section_s))

    if cont:
        # ── Continuous beam: per-location table ──
        _add_continuous_bending_table(content, cont, des, pw)
    else:
        # ── Single span: one-section table ──
        _add_single_bending_table(content, des, reinf, res, pw)

    content.append(Spacer(1, 6))

    # ══════════════════════════════════════════
    #  6. SHEAR DESIGN TABLE
    # ══════════════════════════════════════════
    content.append(Paragraph("SHEAR REINFORCEMENT DESIGN (BS 8110)", section_s))

    shear_rows = [
        [_b("Parameter"), _b("Value"), _b("Parameter"), _b("Value")],
        ["V (Ultimate Shear)", f"{sd.get('V_kN', 'N/A')} kN",
         "v (Shear Stress)", f"{sd.get('v', 'N/A')} N/mm²"],
        ["v_max (Ultimate Limit)", f"{sd.get('v_max', 'N/A')} N/mm²",
         "v_c (Concrete Capacity)", f"{sd.get('vc', 'N/A')} N/mm²"],
        ["Link Type", str(sd.get("link_type", "N/A")).title(),
         "Stirrups", sd.get("link_description", "N/A")],
        ["Status", sd.get("message", "N/A"), "", ""],
    ]
    st = Table(shear_rows, colWidths=[pw * 0.22, pw * 0.28, pw * 0.22, pw * 0.28])
    st.setStyle(_grid_style(header_row=True))

    # Colour the status cell
    status_msg = sd.get("message", "")
    if "SAFE" in str(status_msg).upper() or "minimum" in str(status_msg).lower():
        st.setStyle(TableStyle([("TEXTCOLOR", (1, 4), (1, 4), PASS_COLOR)]))

    content.append(st)
    content.append(Spacer(1, 6))

    # ══════════════════════════════════════════
    #  7. DEFLECTION CHECK TABLE
    # ══════════════════════════════════════════
    content.append(Paragraph("DEFLECTION CHECK (BS 8110 Table 3.9)", section_s))

    defl_status = defl.get("status", "N/A")
    is_pass = defl_status == "SAFE"

    defl_rows = [
        [_b("Parameter"), _b("Value"), _b("Parameter"), _b("Value")],
        ["Basic span/d ratio", str(defl.get("basic_ratio", "N/A")),
         "Service Stress (fs)", f"{defl.get('fs', 'N/A')} N/mm²"],
        ["Modification Factor", str(defl.get("MF", "N/A")),
         "MF (uncapped)", str(defl.get("MF_uncapped", "N/A"))],
        ["Allowable span/d", str(defl.get("allowable_ratio", "N/A")),
         "Actual span/d", str(defl.get("actual_ratio", "N/A"))],
        ["Adjusted", "Yes" if defl.get("fixed") else "No", "", ""],
        ["Status", defl.get("message", "N/A"), "", ""],
    ]
    dt = Table(defl_rows, colWidths=[pw * 0.22, pw * 0.28, pw * 0.22, pw * 0.28])
    dt.setStyle(_grid_style(header_row=True))
    dt.setStyle(TableStyle([
        ("TEXTCOLOR", (1, 5), (1, 5), PASS_COLOR if is_pass else FAIL_COLOR),
        ("FONTNAME", (1, 5), (1, 5), "Helvetica-Bold"),
    ]))
    content.append(dt)
    content.append(Spacer(1, 6))

    # ══════════════════════════════════════════
    #  8. REINFORCEMENT SCHEDULE
    # ══════════════════════════════════════════
    content.append(Paragraph("REINFORCEMENT SCHEDULE", section_s))

    if cont:
        _add_continuous_reinf_schedule(content, cont, reinf, pw)
    else:
        _add_single_reinf_schedule(content, des, reinf, res, pw)

    # ══════════════════════════════════════════
    #  FOOTER
    # ══════════════════════════════════════════
    content.append(Spacer(1, 12))
    content.append(Paragraph(
        "Generated by AI Structural Design System (Software) — A Final Year Project © 2026",
        note_s))

    doc.build(content, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return filename


def _add_page_number(canvas_obj, doc):
    """Draw page number at the bottom-right of every page."""
    page_num = canvas_obj.getPageNumber()
    text = f"Page {page_num}"
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#64748b"))
    canvas_obj.drawRightString(A4[0] - 10 * mm, 8 * mm, text)
    canvas_obj.restoreState()


# ════════════════════════════════════════════
#  HELPER: Single-span bending table
# ════════════════════════════════════════════
def _add_single_bending_table(content, des, reinf, res, pw):
    """Add a single-span bending design table."""
    rows = [
        [_b("Parameter"), _b("Symbol"), _b("Value"), _b("Unit")],
        ["Design Moment", "M", f"{des.get('M', 'N/A')}", "kNm"],
        ["Moment of Resistance", "Mu", f"{des.get('Mu', 'N/A')}", "kNm"],
        ["Effective Depth", "d", f"{des.get('d', 'N/A')}", "mm"],
        ["K = M/(fcu·b·d²)", "K", f"{des.get('K', 'N/A')}", "—"],
        ["K' (limit)", "K'", "0.156", "—"],
        ["Lever Arm", "z", f"{des.get('z', 'N/A')}", "mm"],
        ["As required", "As_req", f"{res.get('steel_area', 'N/A')}", "mm²"],
        ["As provided", "As_prov", f"{reinf.get('provided_area', 'N/A')}", "mm²"],
        ["Reinforcement", "Bars", reinf.get("recommended", "N/A"), "—"],
        ["Section Status", "—", des.get("message", "N/A"), "—"],
    ]

    t = Table(rows, colWidths=[pw * 0.35, pw * 0.15, pw * 0.30, pw * 0.20])
    t.setStyle(_grid_style(header_row=True))

    # Colour status row
    msg = des.get("message", "")
    if "adequate" in str(msg).lower() or "ok" in str(msg).lower():
        t.setStyle(TableStyle([("TEXTCOLOR", (2, 10), (2, 10), PASS_COLOR)]))

    content.append(t)


# ════════════════════════════════════════════
#  HELPER: Continuous beam bending table
# ════════════════════════════════════════════
def _add_continuous_bending_table(content, cont, des, pw):
    """Add per-location bending table for continuous beams."""
    sup_designs = cont.get("support_designs", [])
    span_designs = cont.get("span_designs", [])

    # -- Top Edge (Hogging — support moments) --
    content.append(Paragraph("<b>Bending — Top Edge (Hogging at Supports)</b>", _p(8, colors.black, TA_LEFT)))
    top_header = [_b("Location"), _b("M (kNm)"), _b("K"), _b("z (mm)"),
                  _b("As_req (mm²)"), _b("As_prov (mm²)"), _b("Bars")]
    top_rows = [top_header]

    for d in sup_designs:
        if d.get("As_req", 0) > 0.01:
            top_rows.append([
                d.get("location", ""),
                f"{d.get('M', 0):.2f}",
                f"{d.get('K', 0):.5f}",
                f"{d.get('z', 0):.1f}",
                f"{d.get('As_req', 0):.1f}",
                f"{d.get('As_prov', 0):.1f}",
                d.get("reinforcement", "N/A"),
            ])
        else:
            top_rows.append([d.get("location", ""), "0.00", "—", "—", "—", "—", "N/A"])

    cols = pw / 7
    tt = Table(top_rows, colWidths=[cols] * 7)
    tt.setStyle(_grid_style(header_row=True))
    content.append(tt)
    content.append(Spacer(1, 4))

    # -- Bottom Edge (Sagging — span moments) --
    content.append(Paragraph("<b>Bending — Bottom Edge (Sagging at Spans)</b>", _p(8, colors.black, TA_LEFT)))
    bot_header = [_b("Location"), _b("M (kNm)"), _b("K"), _b("z (mm)"),
                  _b("As_req (mm²)"), _b("As_prov (mm²)"), _b("Bars")]
    bot_rows = [bot_header]

    for d in span_designs:
        bot_rows.append([
            d.get("location", ""),
            f"{d.get('M', 0):.2f}",
            f"{d.get('K', 0):.5f}",
            f"{d.get('z', 0):.1f}",
            f"{d.get('As_req', 0):.1f}",
            f"{d.get('As_prov', 0):.1f}",
            d.get("reinforcement", "N/A"),
        ])

    bt = Table(bot_rows, colWidths=[cols] * 7)
    bt.setStyle(_grid_style(header_row=True))
    content.append(bt)
    content.append(Spacer(1, 4))

    # -- Support Moments & Reactions Summary --
    moments = cont.get("support_moments", [])
    reactions = cont.get("reactions", [])

    if moments or reactions:
        content.append(Paragraph("<b>Support Moments & Reactions</b>", _p(8, colors.black, TA_LEFT)))
        sr_header = [_b("Support")]
        sr_row_m = ["Moment (kNm)"]
        sr_row_r = ["Reaction (kN)"]

        n = max(len(moments), len(reactions))
        for i in range(n):
            label = chr(65 + i)
            sr_header.append(_b(label))
            sr_row_m.append(f"{moments[i]:.2f}" if i < len(moments) else "—")
            sr_row_r.append(f"{reactions[i]:.2f}" if i < len(reactions) else "—")

        sr_t = Table([sr_header, sr_row_m, sr_row_r],
                     colWidths=[pw * 0.18] + [pw * 0.82 / n] * n)
        sr_t.setStyle(_grid_style(header_row=True))
        content.append(sr_t)


# ════════════════════════════════════════════
#  HELPER: Reinforcement schedule (single)
# ════════════════════════════════════════════
def _add_single_reinf_schedule(content, des, reinf, res, pw):
    """Single-span reinforcement schedule table."""
    rows = [
        [_b("Element"), _b("Location"), _b("Size"), _b("As (mm²)"), _b("Status")],
        ["Main Bars (Bottom)", "Mid-span", reinf.get("recommended", "N/A"),
         str(reinf.get("provided_area", "N/A")), _pass_fail(reinf.get("provided_area", 0), res.get("steel_area", 0))],
        ["Top Bars", "Supports", "2Y12 (nominal)", "226", "Nominal"],
    ]

    # Add shear links from shear_design if available
    sd = des if "link_description" in des else {}

    t = Table(rows, colWidths=[pw * 0.22, pw * 0.18, pw * 0.22, pw * 0.18, pw * 0.20])
    t.setStyle(_grid_style(header_row=True))

    # Colour status
    prov = reinf.get("provided_area", 0)
    req = res.get("steel_area", 0)
    if prov and req and prov >= req:
        t.setStyle(TableStyle([("TEXTCOLOR", (4, 1), (4, 1), PASS_COLOR)]))

    content.append(t)


# ════════════════════════════════════════════
#  HELPER: Reinforcement schedule (continuous)
# ════════════════════════════════════════════
def _add_continuous_reinf_schedule(content, cont, reinf, pw):
    """Continuous beam reinforcement schedule with per-location bars."""
    sup_designs = cont.get("support_designs", [])
    span_designs = cont.get("span_designs", [])

    header = [_b("Location"), _b("Type"), _b("Bars"),
              _b("As_req (mm²)"), _b("As_prov (mm²)"), _b("Status")]
    rows = [header]

    # Top bars at supports (hogging)
    for d in sup_designs:
        if d.get("As_req", 0) > 0.01:
            status = _pass_fail(d.get("As_prov", 0), d.get("As_req", 0))
            rows.append([
                d.get("location", ""),
                "Top (Hogging)",
                d.get("reinforcement", "N/A"),
                f"{d.get('As_req', 0):.1f}",
                f"{d.get('As_prov', 0):.1f}",
                status,
            ])

    # Bottom bars at spans (sagging)
    for d in span_designs:
        status = _pass_fail(d.get("As_prov", 0), d.get("As_req", 0))
        rows.append([
            d.get("location", ""),
            "Bottom (Sagging)",
            d.get("reinforcement", "N/A"),
            f"{d.get('As_req', 0):.1f}",
            f"{d.get('As_prov', 0):.1f}",
            status,
        ])

    cols = pw / 6
    t = Table(rows, colWidths=[cols] * 6)
    t.setStyle(_grid_style(header_row=True))

    # Colour status column green/red
    for i in range(1, len(rows)):
        status_text = rows[i][5]
        if "OK" in str(status_text):
            t.setStyle(TableStyle([("TEXTCOLOR", (5, i), (5, i), PASS_COLOR)]))

    content.append(t)


# ════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ════════════════════════════════════════════
def _p(size, colour, align=TA_LEFT):
    """Create a quick ParagraphStyle."""
    return ParagraphStyle("_auto", fontSize=size, textColor=colour,
                          alignment=align, fontName="Helvetica")


def _b(text):
    """Wrap text in bold Paragraph for table cells."""
    return Paragraph(f"<b>{text}</b>",
                     ParagraphStyle("_b", fontSize=8, fontName="Helvetica-Bold"))


def _pass_fail(provided, required):
    """Return OK or FAIL string."""
    try:
        if float(provided) >= float(required):
            return "OK ✓"
        return "FAIL ✗"
    except (TypeError, ValueError):
        return "—"


def _grid_style(header_row=False):
    """Standard grid table style."""
    cmds = [
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if header_row:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), SECTION_BG),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#475569")),
        ]
    return TableStyle(cmds)
