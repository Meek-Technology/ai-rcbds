# AI-RCBDS: AI Reinforced Concrete Beam Design System

**AI-RCBDS** is a state-of-the-art, machine-learning-powered structural engineering application designed to automate the complete analysis and design of reinforced concrete beams according to **BS 8110** standards. It features an advanced Natural Language Processing (NLP) multi-load prompt parser interface, allowing structural engineers and students to input complex, multi-span, multi-load scenarios in plain English and instantly receive rigorous engineering design calculations, interactive SFD/BMD/Load diagrams, auto-resized beam recommendations, and professional PDF calculation sheets.

This project was developed as a Final Year Civil Engineering Research Project at **Federal University Oye-Ekiti (FUOYE)** by **Engr. Micheal Shokunbi** under **MEEK Technology**.

---

## 🌟 Core Features & Structural Capabilities

*   **Natural Language Multi-Load Prompt Interface**: Express complex structural inputs naturally (e.g., *"3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m"*).
*   **Heterogeneous Multi-Load Engineering Engine**: Full support for single-span and multi-span continuous systems carrying combinations of:
    *   Uniformly Distributed Loads (UDLs) over full spans
    *   Partial UDLs with specific start/end locations
    *   Multiple Concentrated Point Loads at arbitrary locations
    *   Self-weight and factored wall line loads (density $\times$ thickness $\times$ height)
*   **Comprehensive BS 8110 Structural Analysis**:
    *   Superposition principle calculations for moment ($M_{udl} + \sum M_{point}$) and shear ($V_{udl} + \sum V_{point}$)
    *   Three-Moment Theorem matrix solver for statically indeterminate continuous beams
    *   Flexural reinforcement design ($K, z, A_{s,req}, A_{s,min}, A_{s,provided}$)
    *   Shear stress compliance & link reinforcement design ($v, v_c, A_{sv}/s_v$)
    *   Deflection checks ($L/d$ basic and allowable limits per BS 8110 Table 3.9)
    *   Automatic iterative beam resizing when initial section dimensions fail deflection or shear criteria
*   **Supported Beam Configuration Types**:
    1.  **Simply Supported Beams** (Pinned - Roller)
    2.  **Cantilever Beams** (Fixed - Free End)
    3.  **Overhanging Beams** (Interior span with cantilever extension)
    4.  **Multi-Span Continuous Beams** (2 to 5 spans with flexible support boundary conditions)
*   **Interactive Visualizations**:
    *   Dynamic HTML5 Canvas structural loading diagrams with standard engineering support symbols
    *   High-resolution Chart.js plots for Shear Force Diagrams (SFD) and Bending Moment Diagrams (BMD) with peak annotations
*   **Professional Engineering Documentation**:
    *   **BS 8110 Calculation Sheet PDF**: Complete step-by-step mathematical breakdown with formulas, design moments, steel areas, link selection, and deflection checks.
    *   **Design Results Summary Report PDF**: Executive structural summary report for project documentation.

---

## 💻 Tech Stack

*   **Backend Architecture**: Python 3.12+, FastAPI, Uvicorn (Asynchronous REST API)
*   **Structural Mechanics Engine**: Custom Linear Superposition & Three-Moment Theorem Solvers
*   **Machine Learning Model**: RandomForest & XGBoost Ensembles (trained on 10,000+ BS 8110 compliant beam designs)
*   **PDF Generation Suite**: ReportLab 4.x with Pillow image compositing
*   **Frontend UI/UX**: HTML5, Vanilla CSS3 (Glassmorphism & Cyberpunk Industrial Dark Aesthetic), Vanilla JavaScript (ES6+), Chart.js 4.4

---

## 🚀 Installation & Running Locally

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Meek-Technology/ai-rcbds.git
    cd ai-rcbds
    ```

2.  **Set Up Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Linux/macOS
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch the Application**:
    ```bash
    uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
    ```

5.  **Access Web Application**: Open `http://127.0.0.1:8000` in your web browser.

---

## 📝 Example Prompts for Testing

### 1. Simply Supported Beam (UDL + Point Load)
`Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m`

### 2. Simply Supported Beam (Multiple Point Loads)
`Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m`

### 3. Partial UDL + Point Load
`Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m`

### 4. Overhang Beam (UDL + Free End Point Load)
`Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end`

### 5. Overhang Beam (Multiple Point Loads)
`Overhang beam 5m span, 1.5m overhang, point loads 20kN at 3m and 15kN at 6.5m`

### 6. Continuous Beam (3 Spans with Heterogeneous Loading)
`3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m`

### 7. Continuous Beam (2 Spans with Mixed Loads)
`Continuous beam spans 4m and 5m, UDL 18kN/m on first span, point load 35kN at 2.5m on second span`

### 8. Cantilever Beam
`Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m`

---

## 📄 License & Attribution
Developed by **Engr. Micheal Shokunbi** under **MEEK Technology** for the **AI Reinforced Concrete Beam Design System (AI-RCBDS)** project. All rights reserved.