"""Generate PDF presentation guide from the markdown content."""
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "AI_Presentation_Guide.pdf")

def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm,
                            leftMargin=18*mm, rightMargin=18*mm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_s = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=22,
                             textColor=colors.HexColor("#1e3a5f"), spaceAfter=6)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16,
                        textColor=colors.HexColor("#1e3a5f"), spaceBefore=14, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13,
                        textColor=colors.HexColor("#2d6a4f"), spaceBefore=10, spaceAfter=4)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11,
                        textColor=colors.HexColor("#555555"), spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10,
                          leading=14, spaceAfter=4)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=16, bulletIndent=6,
                            spaceAfter=2)
    code_s = ParagraphStyle("Code", parent=body, fontName="Courier", fontSize=9,
                            backColor=colors.HexColor("#f0f0f0"), leftIndent=10,
                            spaceAfter=4, leading=12)
    speaker = ParagraphStyle("Speaker", parent=body, fontName="Helvetica-Oblique",
                             fontSize=9.5, textColor=colors.HexColor("#444444"),
                             leftIndent=14, borderColor=colors.HexColor("#2d6a4f"),
                             borderWidth=1, borderPadding=6, spaceAfter=6)
    sub_s = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10,
                           textColor=colors.HexColor("#555555"), alignment=TA_CENTER)

    def tbl(data, col_widths=None):
        """Helper to create a styled table."""
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7f7f7"), colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return t

    S = Spacer(1, 6)
    HR = HRFlowable(width="100%", color=colors.HexColor("#cccccc"), thickness=1, spaceAfter=8)

    c = []  # content list

    # ── COVER ──
    c.append(Spacer(1, 60))
    c.append(Paragraph("AI Structural Design", title_s))
    c.append(Paragraph("Seminar Presentation Guide", ParagraphStyle("sub2", parent=title_s, fontSize=15, textColor=colors.HexColor("#2d6a4f"))))
    c.append(Spacer(1, 12))
    c.append(Paragraph("Date: May 9, 2026 &nbsp;|&nbsp; Project: AI Structural Beam Design System &nbsp;|&nbsp; Developer: MEEK Technology", sub_s))
    c.append(Spacer(1, 30))
    c.append(HR)

    # ── OVERVIEW ──
    c.append(Paragraph("Presentation Overview", h1))
    c.append(Paragraph("This guide covers the <b>AI logic</b> in the project. The system combines <b>three AI/intelligent techniques</b>:", body))
    c.append(tbl([
        ["#", "Technique", "Where in Code", "Purpose"],
        ["1", "NLP Prompt Parsing", "nlp/prompt_parser.py", "Extracts structural parameters from natural language"],
        ["2", "Machine Learning Prediction", "model/train_model.py + model.pkl", "Predicts required steel reinforcement area"],
        ["3", "Rule-Based Expert System", "rules/beam_design.py + continuous_beam.py", "Engineering calculations per BS 8110"],
    ], col_widths=[20, 110, 140, 200]))
    c.append(S)

    # ── SLIDE 1 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 1: System Architecture (The Big Picture)", h1))
    c.append(Paragraph("<b>What to Present:</b> Show the end-to-end pipeline:", body))
    c.append(Paragraph("User types prompt &rarr; NLP Parser &rarr; Parse Modal (User confirms) &rarr; Rule Engine (BS 8110) &rarr; ML Model (Random Forest) &rarr; Results + Diagrams &rarr; PDF Report", code_s))
    c.append(Paragraph("<b>Key Points to Emphasize:</b>", body))
    for b_text in [
        "<b>Hybrid AI</b> = NLP + ML + Expert System working together",
        "The system is accessed via a <b>FastAPI web API</b> (api/main.py)",
        "Two-step user flow: <b>Parse &rarr; Confirm &rarr; Generate</b> (not a black box)",
        "The user always gets to <b>verify</b> what the AI understood before running calculations",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))
    c.append(S)
    c.append(Paragraph("<b>Speaker Notes:</b>", h3))
    c.append(Paragraph('"Our system uses a hybrid AI approach. Rather than relying on a single AI technique, we combine three complementary methods: NLP for understanding user input, machine learning for prediction, and a rule-based expert system for engineering compliance. This makes the system both intelligent AND reliable."', speaker))

    # ── SLIDE 2 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 2: NLP Prompt Parsing \u2014 How the System Understands You", h1))
    c.append(Paragraph("The NLP module (nlp/prompt_parser.py) uses <b>regex-based Natural Language Processing</b> to extract 15+ structural parameters from free-text prompts.", body))
    c.append(Paragraph("<b>Example Demo:</b>", h2))
    c.append(Paragraph('Input: "Design a simply supported beam with span 6m and load 25kN/m"', code_s))
    c.append(Paragraph("Extracted: beam_type=simply_supported, load_type=udl, span=6.0, load=25.0, fcu=25, fy=460, support_left=pinned, support_right=roller", code_s))

    c.append(Paragraph("extract_parameters(text) \u2014 The Brain", h2))
    for b_text in [
        "Uses <b>20+ regex patterns</b> to scan the prompt",
        "Extracts: span, load, beam type, load type, supports, material grades, wall properties, overhang length, multi-span data",
        'If "overhang" keyword found &rarr; auto-sets beam_type = "overhang"',
        'If "point load" value found &rarr; overrides load_type to "point_load"',
        'If "free end" detected on overhang &rarr; calculates load_position = span + overhang_length',
        'If "continuous" with no explicit spans &rarr; replicates single span based on n_span_match',
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(Paragraph("apply_defaults(params) \u2014 The Safety Net", h2))
    for b_text in [
        "Fills in missing values with <b>engineering defaults</b>: fcu=25, fy=460, wall unit weight=20.0",
        "<b>Validates</b> that span and load are provided (raises ValueError if missing)",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(Paragraph("<b>Key Regex Patterns:</b>", h3))
    c.append(tbl([
        ["What it Finds", "Input Example"],
        ["Span", '"span 6m" or "span of 6m"'],
        ["Multiple spans", '"spans 6m, 5m, 4m"'],
        ["Beam type", '"cantilever beam", "continuous"'],
        ["Point load", '"point load of 50kN"'],
        ["Support types", '"supports: pinned, fixed, roller"'],
    ], col_widths=[120, 350]))

    c.append(Paragraph("<b>The Parse Modal (Two-Step Safety):</b>", h3))
    for i, b_text in enumerate([
        'User types prompt &rarr; clicks "Generate Design"',
        "Frontend calls /parse (lightweight \u2014 only runs NLP, no calculations)",
        "<b>Modal pops up</b> showing all extracted parameters",
        'User reviews &rarr; clicks "Confirm" &rarr; full /predict runs',
        'If wrong &rarr; user clicks "Cancel" and rephrases',
    ], 1):
        c.append(Paragraph(f"{i}. {b_text}", body))

    c.append(Paragraph("<b>Speaker Notes:</b>", h3))
    c.append(Paragraph('"The NLP component doesn\'t use a large language model \u2014 it uses pattern matching with regular expressions. This is a deliberate design choice for a structural engineering tool: regex gives us deterministic, predictable extraction. We can\'t afford hallucinated values in engineering calculations."', speaker))

    # ── SLIDE 3 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 3: Machine Learning Model \u2014 Steel Area Prediction", h1))
    c.append(Paragraph("The ML component uses a <b>Random Forest Regressor</b> (scikit-learn) trained on <b>5,000 synthetic beam design samples</b>.", body))

    c.append(Paragraph("<b>Training Pipeline:</b>", h2))
    c.append(Paragraph("data/generate_data.py (5000 samples) &rarr; beam_dataset.csv &rarr; model/train_model.py (Random Forest) &rarr; model.pkl (45 MB) &rarr; api/main.py (runtime prediction)", code_s))

    c.append(Paragraph("<b>Training Data Generation</b> (data/generate_data.py):", h3))
    c.append(Paragraph("span = random.uniform(3, 10) | load = random.uniform(10, 50) | fck = choice([20,25,30]) | fy = 460", code_s))
    c.append(Paragraph("Each sample runs through the rule-based design_beam() to get the correct steel area &rarr; becomes the training label.", body))

    c.append(Paragraph("<b>The Model</b> (model/train_model.py):", h3))
    c.append(Paragraph("model = RandomForestRegressor(n_estimators=100); model.fit(X, y)", code_s))
    for b_text in [
        "<b>Algorithm:</b> Random Forest Regressor (ensemble of 100 decision trees)",
        "<b>Features (inputs):</b> span, load, fck, fy",
        "<b>Target (output):</b> steel_area (mm\u00b2)",
        "<b>Serialization:</b> Saved with joblib as model.pkl (~45 MB)",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(Paragraph("<b>Runtime Prediction</b> (api/main.py):", h3))
    c.append(Paragraph('input_df = pd.DataFrame([{"span": span, "load": max(w, 1), "fck": fck, "fy": fy}])\nsteel_area = model.predict(input_df)[0]', code_s))

    c.append(Paragraph("<b>Speaker Notes:</b>", h3))
    c.append(Paragraph('"Why use ML if we already have rule-based calculations? The ML model serves as a rapid estimator and cross-validator. It was trained on data generated by our own rule engine, so it learns the relationship between structural parameters and required reinforcement. The Random Forest was chosen because it handles non-linear relationships well, is robust to outliers, and doesn\'t require feature scaling."', speaker))

    c.append(Paragraph("<b>Anticipated Q&amp;A:</b>", h3))
    c.append(tbl([
        ["Question", "Answer"],
        ["Why Random Forest?", "Handles non-linear relationships, no feature scaling needed, interpretable"],
        ["Why synthetic data?", "Real beam design data is scarce; our rule engine generates ground-truth labels"],
        ["How accurate is it?", "Trained on rule-engine output, so it mirrors BS 8110 calculations closely"],
        ["Why 100 trees?", "Standard default; good bias-variance tradeoff without overfitting"],
        ["Model size 45MB?", "100 decision trees with 5000 samples; acceptable for server deployment"],
    ], col_widths=[150, 320]))

    # ── SLIDE 4 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 4: Rule-Based Expert System (BS 8110)", h1))
    c.append(Paragraph("The engineering calculations follow <b>BS 8110</b> (British Standard for structural concrete design). This is the deterministic backbone of the system.", body))

    c.append(Paragraph("<b>Load Calculation Pipeline:</b>", h2))
    c.append(Paragraph("User Load (n1) + Beam Self-Wt (n2) + Wall Load (n3) = w (Total UDL) &rarr; Design Moment &rarr; Steel Area &rarr; Reinforcement Selection", code_s))

    c.append(Paragraph("<b>Key Functions:</b>", h3))
    c.append(tbl([
        ["Function", "Purpose", "Formula"],
        ["calc_beam_self_weight()", "Factored self-weight", "n2 = 1.4 \u00d7 b \u00d7 d \u00d7 24"],
        ["calc_wall_load()", "Wall line load & factored wall load", "Wall Line Load = UW × t × h; n3 = 1.4 × WLL"],
        ["design_loads()", "Combines all loads", "w = n1 + n2 + n3"],
        ["bending_moment()", "Max BM for beam type", "Varies by type"],
        ["max_shear_force()", "Maximum shear", "Varies by type"],
        ["estimate_beam_size()", "Standard dimensions", "Based on span/depth ratio"],
        ["recommend_reinforcement()", "Optimal bar combo", "Minimizes excess area"],
    ], col_widths=[145, 130, 195]))

    c.append(Paragraph("<b>Bending Moment Formulas:</b>", h3))
    c.append(tbl([
        ["Beam Type", "UDL", "Point Load"],
        ["Simply Supported", "M = wL\u00b2/8", "M = Pa(L\u2212a)/L"],
        ["Cantilever", "M = wL\u00b2/2", "M = Pa"],
        ["Continuous", "M = wL\u00b2/12", "M = Pa(L\u2212a)/L \u00d7 0.8"],
        ["Overhang", "Complex (reactions first)", "P \u00d7 overhang at support"],
    ], col_widths=[120, 175, 175]))

    c.append(Paragraph("<b>Beam Size Estimation:</b>", h3))
    for b_text in [
        "<b>Widths:</b> 230, 300, 450, 600, 750, 900 mm",
        "<b>Depths:</b> 300, 450, 600, 750, 900, 1050, 1200 mm",
        "<b>Rule:</b> Minimum depth = span \u00d7 1000 / deflection_limit",
        "<b>Deflection limits:</b> Simply Supported = L/20, Cantilever = L/7, Continuous = L/26",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(Paragraph("<b>Reinforcement Selection:</b> For each bar size (10, 12, 16, 20, 25 mm): calculate area per bar, bars needed, provided area. Select minimum provided area meeting requirement. Output format: 3Y16 = 3 bars of 16mm.", body))

    c.append(Paragraph("<b>Speaker Notes:</b>", h3))
    c.append(Paragraph('"The rule engine is the most critical component. While the ML model provides predictions, the rule engine provides certainty. Every calculation follows BS 8110 partial safety factors \u2014 1.4 for dead loads, 1.6 for live loads. The system also performs deflection checks using span-to-depth ratios."', speaker))

    # ── SLIDE 5 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 5: Three-Moment Theorem \u2014 Continuous Beam Solver", h1))
    c.append(Paragraph("The most advanced engineering feature \u2014 solving <b>statically indeterminate</b> multi-span beams using <b>Clapeyron's Three-Moment Theorem</b>.", body))

    c.append(Paragraph("<b>The Problem:</b>", h2))
    c.append(Paragraph("Simply supported beams are statically determinate. Continuous beams (multiple spans) are <b>indeterminate</b> \u2014 more unknowns than equilibrium equations. The Three-Moment Theorem provides additional equations by enforcing <b>slope compatibility</b> at each internal support.", body))

    c.append(Paragraph("<b>Algorithm Flow:</b>", h2))
    c.append(Paragraph("Input (spans, loads, supports) &rarr; Compute loading terms (6A\u0101/L, 6Ab\u0304/L) &rarr; Build coefficient matrix [A]\u00d7{M}={b} &rarr; Solve (numpy.linalg.solve) &rarr; Support moments &rarr; Reactions &rarr; SFD &amp; BMD", code_s))

    c.append(Paragraph("<b>The Three-Moment Equation:</b>", h3))
    c.append(Paragraph("M(i-1)\u00b7L_left + 2\u00b7M(i)\u00b7(L_left + L_right) + M(i+1)\u00b7L_right = \u2212(6A\u0101/L_right + 6Ab\u0304/L_left)", code_s))

    c.append(Paragraph("<b>Loading Terms:</b>", h3))
    c.append(tbl([
        ["Load Type", "6A\u0101/L (left term)", "6Ab\u0304/L (right term)"],
        ["UDL (w)", "wL\u00b3/4", "wL\u00b3/4 (symmetric)"],
        ["Point Load (P at a)", "Pa(L\u00b2\u2212a\u00b2)/L", "Pb\u00b7a(2L\u2212a)/L"],
    ], col_widths=[130, 170, 170]))

    c.append(Paragraph("<b>Boundary Conditions:</b>", h3))
    c.append(tbl([
        ["Support Type", "Moment Condition"],
        ["Pinned / Roller", "M = 0 (known)"],
        ["Fixed", "M \u2260 0 (unknown \u2014 adds equation)"],
    ], col_widths=[150, 320]))

    c.append(Paragraph("<b>Key Implementation Details:</b>", h3))
    for b_text in [
        "<b>Matrix assembly</b> \u2014 builds [A]\u00b7{M} = {b} for all unknown moments",
        "<b>Fixed-end handling</b> \u2014 adds extra equations using imaginary zero-length span",
        "<b>NumPy solver</b> \u2014 np.linalg.solve() for the linear system",
        "<b>Reaction computation</b> \u2014 per-span moment equilibrium after solving moments",
        "<b>Diagram generation</b> \u2014 30 points per span, merged into continuous arrays",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(Paragraph("<b>Speaker Notes:</b>", h3))
    c.append(Paragraph('"The Three-Moment Theorem is a classical structural analysis method, but implementing it programmatically required building a general-purpose linear algebra solver. Our system handles any number of spans (up to 5), any combination of UDL and point loads per span, and mixed support conditions including fixed ends."', speaker))

    # ── SLIDE 6 ──
    c.append(PageBreak())
    c.append(Paragraph("SLIDE 6: Visualization &amp; Output", h1))
    c.append(Paragraph("The frontend renders:", body))
    for b_text in [
        "<b>Beam diagram</b> \u2014 supports and loads on HTML5 Canvas",
        "<b>Shear Force Diagram (SFD)</b> \u2014 using Chart.js",
        "<b>Bending Moment Diagram (BMD)</b> \u2014 peak highlighted in red",
        "<b>Load Diagram</b> \u2014 distributed load profile",
        "<b>PDF Report</b> \u2014 generated server-side with ReportLab",
    ]:
        c.append(Paragraph(b_text, bullet, bulletText="\u2022"))

    c.append(tbl([
        ["Component", "Technology"],
        ["UI Framework", "Vanilla HTML/CSS/JS"],
        ["Charts", "Chart.js (line charts with animations)"],
        ["Beam Diagram", "HTML5 Canvas API"],
        ["HTTP Client", "Fetch API"],
        ["PDF Generation", "ReportLab (Python, server-side)"],
    ], col_widths=[150, 320]))

    # ── SLIDE 7 ──
    c.append(Paragraph("SLIDE 7: System Features Summary", h1))
    c.append(tbl([
        ["Feature", "Status", "AI Technique"],
        ["Natural language input", "\u2713", "NLP (Regex)"],
        ["Parameter verification modal", "\u2713", "NLP + UX"],
        ["Steel area prediction", "\u2713", "ML (Random Forest)"],
        ["Beam sizing (BS 8110)", "\u2713", "Rule-based"],
        ["Load factoring (BS 8110)", "\u2713", "Rule-based"],
        ["Deflection check", "\u2713", "Rule-based"],
        ["Reinforcement selection", "\u2713", "Algorithmic"],
        ["Simply supported beams", "\u2713", "Rule-based"],
        ["Cantilever beams", "\u2713", "Rule-based"],
        ["Overhang beams", "\u2713", "Rule-based"],
        ["Continuous beams (multi-span)", "\u2713", "Three-Moment Theorem"],
        ["UDL, Point Load, Triangular", "\u2713", "Rule-based"],
        ["SFD / BMD / Load diagrams", "\u2713", "Algorithmic + Chart.js"],
        ["PDF report generation", "\u2713", "ReportLab"],
        ["REST API", "\u2713", "FastAPI"],
    ], col_widths=[195, 50, 225]))

    # ── PRESENTATION TIPS ──
    c.append(PageBreak())
    c.append(Paragraph("Presentation Tips", h1))

    c.append(Paragraph("<b>Recommended Structure (15\u201320 minutes):</b>", h2))
    c.append(tbl([
        ["Time", "Slide", "Focus"],
        ["0\u20132 min", "Architecture", "Big picture \u2014 hybrid AI approach"],
        ["2\u20135 min", "NLP Parser", "Live demo with example prompts"],
        ["5\u20138 min", "ML Model", "Training pipeline, Random Forest, prediction"],
        ["8\u201312 min", "Rule Engine", "BS 8110 calculations, beam types"],
        ["12\u201315 min", "Three-Moment", "Continuous beam solver (strongest feature)"],
        ["15\u201317 min", "Visualization", "Show diagrams, charts, PDF"],
        ["17\u201320 min", "Q&A", "Use prepared answers"],
    ], col_widths=[70, 100, 300]))

    c.append(Paragraph("<b>Live Demo Script:</b>", h2))
    for i, t in enumerate([
        "Open the web UI",
        'Type: "Design a simply supported beam with span 6m and load 25kN/m"',
        "Show the parse modal \u2014 explain each extracted parameter",
        "Click Confirm \u2014 show results, diagrams, reinforcement",
        'Type: "Design a continuous beam with spans 6m, 5m, 4m and UDL 20kN/m"',
        "Show the multi-span diagram with support moments and reactions",
        "Download the PDF report",
    ], 1):
        c.append(Paragraph(f"{i}. {t}", body))

    c.append(Paragraph("<b>Common Q&amp;A Preparation:</b>", h2))
    c.append(tbl([
        ["Question", "Suggested Answer"],
        ["Why not use ChatGPT/LLM?", "Deterministic regex ensures no hallucinated values. Safety-critical."],
        ["Is the ML model accurate?", "Trained on BS 8110-compliant data. Both ML and rules shown."],
        ["Real-world loads?", "Handles UDL, point, triangular, wall, slab loads with BS 8110 factoring."],
        ["Other structural elements?", "Architecture is extensible \u2014 columns/slabs could use same pipeline."],
        ["More than 3 spans?", "Matrix system scales dynamically. N\u22121 equations for N spans."],
        ["What code standard?", "BS 8110 with \u03b3_G = 1.4 and \u03b3_Q = 1.6."],
    ], col_widths=[160, 310]))

    c.append(S)
    c.append(Paragraph("<b>Closing Statement (Suggested):</b>", h2))
    c.append(Paragraph('"This project demonstrates that AI in structural engineering doesn\'t have to be a black box. By combining NLP for input understanding, machine learning for rapid estimation, and rule-based engineering for code compliance, we\'ve built a system that is both intelligent and trustworthy. The human-in-the-loop verification step ensures that no structural design proceeds without engineer approval."', speaker))

    c.append(S)
    c.append(HR)
    c.append(Paragraph("<b>Key differentiator:</b> Your system is a <b>hybrid AI</b> \u2014 not just ML, not just rules. The combination of NLP + ML + Expert System is what makes it production-grade for engineering use.", body))
    c.append(Paragraph("<b>Pro tip:</b> Start your presentation with a live demo before diving into theory. Show the working system first \u2014 it creates instant engagement.", body))

    doc.build(c)
    print(f"\nPDF generated successfully: {OUTPUT}")

if __name__ == "__main__":
    build()
