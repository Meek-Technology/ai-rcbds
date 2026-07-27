# AI-RCBDS: AI Reinforced Concrete Beam Design System

**AI-RCBDS** is a state-of-the-art, machine-learning-powered structural engineering application designed to automate the analysis and design of reinforced concrete beams according to **BS 8110** standards. It features a unique Natural Language Processing (NLP) prompt interface, allowing engineers to simply type their design requirements in plain English and instantly receive comprehensive engineering calculations, interactive diagrams, and professional PDF reports.

This system was developed as a Final Year Project to bridge the gap between artificial intelligence and traditional structural engineering workflows.

---

## 🌟 Key Features

*   **Natural Language Prompt Interface**: Describe your beam in plain English (e.g., *"Design a continuous beam with spans 5m, 6m, and 5m, UDL of 15kN/m, supports pinned, roller, roller, pinned"*). The NLP parser intelligently extracts geometry, loads, support conditions, and material properties.
*   **Comprehensive BS 8110 Design**: Full structural analysis including Bending Moment, Shear Force, Required Steel Area ($A_s$), and Deflection Checks (Table 3.9).
*   **Multiple Beam Types**: Supports Simply Supported, Cantilever, Overhang, and Multi-Span Continuous Beams.
*   **Advanced Structural Solvers**: Integrates the **Three-Moment Theorem** for statically indeterminate continuous beams.
*   **Dynamic Visualizations**: 
    *   Interactive HTML5 Canvas beam diagrams with standard engineering symbols.
    *   Chart.js-powered graphical plotting of Load Distributions, Shear Force Diagrams (SFD), and Bending Moment Diagrams (BMD) with peak annotations.
*   **Factored Wall Loading**: Automatically calculates and applies structural wall line loads based on user-provided wall thickness, height, and unit weight.
*   **Professional PDF Exports**: Generates official **Engineering Calculation Sheets** and **Results Reports** via ReportLab, complete with branded headers, custom project titles, and embedded high-resolution diagrams.
*   **AI ML Prediction**: Employs a Random Forest Regressor trained on thousands of simulated designs to benchmark standard mathematical design approaches.

---

## 💻 Tech Stack

*   **Backend Application**: Python 3, FastAPI, Uvicorn
*   **Machine Learning & Data**: Scikit-Learn, Pandas, NumPy, Regex
*   **PDF Generation**: ReportLab, Pillow (Image Compositing)
*   **Frontend UI**: HTML5, Vanilla CSS (Glassmorphism UI), Vanilla JavaScript, Chart.js

---

## 🚀 How to Run

1.  **Clone the Repository** and navigate into the directory.
2.  **Activate your virtual environment** (if applicable).
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start the Server**:
    ```bash
    uvicorn api.main:app --host 127.0.0.1 --port 8000
    ```
5.  **Access the Application**: Open your browser and navigate to `http://127.0.0.1:8000` to launch the beautiful AI-RCBDS interface.

---

## 📝 Example Prompts

Try pasting these directly into the application:
*   `Design a simply supported beam with span 6m, UDL of 25kN/m, fcu 30 and fy 500`
*   `Design a cantilever beam of span 4m, point load 30kN at 4m with fixed support`
*   `Design a continuous beam with spans 5m, 6m, and 5m, UDL of 15kN/m, supports pinned, roller, roller, pinned`
*   `Design an overhang beam with span 7m and overhang 2m, UDL 20kN/m, pinned and roller supports`

---

## 📄 License
This project is proprietary. All rights reserved. See the LICENSE file for details. Developed by Engr. Micheal Shokunbi (MEEK Technology).