# Chapter Four - Implementation & Results


## 4.1 Beam Design Implementation

The beam design module was developed using Python functions to compute structural parameters.

<p align="center">
    <a href="images/Screenshot_2049.png">
        <img src="images/Screenshot_2049.png" alt="Beam design testing result" width="500"/>
    </a>
    <br/>
    <em>Figure 4.1a: Beam design testing result</em>
</p>
<!-- [![Beam design testing result](images/Screenshot_2049.png)](images/Screenshot_2049.png) -->
 
The bending moment for a simply supported beam under uniformly distributed load was calculated using the formula:

Mu = wL² / 8

Where:

- w = load (kN/m)
- L = span (m)

The required steel area was computed using standard reinforcement concrete design equations.

<p align="center">
    <a href="images/Screenshot_2060.png">
        <img src="images/Screenshot_2060.png" alt="Beam design testing code" width="500"/>
    </a>
    <br/>
    <em>Figure 4.1b: Beam design testing code</em>
</p>


## 4.2 Dataset Generation

A dataset was generated using simulated structural parameters to train the AI model.

<p align="center">
    <a href="images/Screenshot_2065.png">
        <img src="images/Screenshot_2065.png" alt="Dataset generation script" width="500" />
    </a>
        <br/>
        <em>Figure 4.2a: Dataset generation script</em>
</p>

<p align="center">
    <a href="images/Screenshot_2066.png">
        <img src="images/Screenshot_2066.png" alt="Dataset generation terminal print" width="500" />
    </a>
    <br/>
    <em>Figure 4.2b: Dataset generation terminal print</em>
</p>

The parameters included:

- Beam span (3m – 10m)
- Load (10 kN/m – 50 kN/m)
- fck (concrete grade 20, 25, 30)
- fy (steel grade 460)

For each generated input, the corresponding steel area was calculated using the standard beam design equations.

A total of 5000 data samples were generated and stored in a CSV file for training purposes.

<p align="center">
    <a href="images/Screenshot_2067.png">
        <img src="images/Screenshot_2067.png" alt="Generated data samples in csv-1" width="45%" />
    </a>
    <a href="images/Screenshot_2068.png">
        <img src="images/Screenshot_2068.png" alt="Generated data samples in csv-2" width="45%" />
    </a>
    <br/>
    <em>Figure 4.2c & 4.2d: Generated data samples in csv</em>
</p>


## 4.3 AI Model Development

A machine learning model was developed to predict the required steel area for beam design based on input parameters.

<p align="center">
    <a href="images/Screenshot_2061.png">
        <img src="images/Screenshot_2061.png" alt="AI model development script" width="500" />
    </a>
    <br/>
    <em>Figure 4.3a: AI model development script</em>
</p>

The dataset generated was used to train the model, with the following features:

- Span
- Load
- fck
- fy

The target output was:

- Steel area

A Random Forest Regression algorithm was used for training due to its ability to handle nonlinear relationships and provide accurate predictions.

<p align="center">
    <a href="images/Screenshot_2062.png">
        <img src="images/Screenshot_2062.png" alt="trained AI model" width="500" />
    </a>
    <br/>
    <em>Figure 4.3b: trained AI model</em>
</p>

The trained model was saved as "model.pkl" and used for making predictions within the system.

The result output from the model was compared with the calculated steel area from the beam design module to evaluate the accuracy of predictions.

<p align="center">
    <a href="images/Screenshot_2069.png">
        <img src="images/Screenshot_2069.png" alt="AI generated Steel Area result" width="500" />
    </a>
    <br/>
    <em>Figure 4.3c: AI generated Steel Area result</em>
</p>


## 4.4 Model Input Features

The AI model was trained using four input features:

- Span
- Load
- Concrete strength/grade (fcu/fck)
- Steel strength/grade (fy)

These parameters were used to improve the accuracy of predictions and better reflect real-world structural design conditions.

The inclusion of both concrete and steel grades allowed the model to learn the influence of material properties on the required steel area for beam design.

<p align="center">
    <a href="images/Screenshot_2071.png">
        <img src="images/Screenshot_2071.png" alt="Model input features" width="500" />
    </a>
    <br/>
    <em>Figure 4.4a: Model input features</em>
</p>


## 4.5 Prompt-Based Input System

A prompt-based input system was developed to allow users to input structural parameters using natural language.

The system extracts key parameters such as:

- Span
- Load
- Concrete strength/grade (fcu/fck)
- Steel strength/grade (fy)

<p align="center">
    <a href="images/Screenshot_2077.png">
        <img src="images/Screenshot_2077.png" alt="Natural language parameters extracter" width="500" />
    </a>
    <br/>
    <em>Figure 4.5a: Natural language parameters extracter</em>
</p>

<p align="center">
    <a href="images/Screenshot_2075.png">
        <img src="images/Screenshot_2075.png" alt="Prompt to parameters testing" width="500" />
    </a>
    <br/>
    <em>Figure 4.5b: Prompt to parameters testing</em>
</p>

Pattern matching techniques using regular expressions were used to identify and extract values from user input.

Default values were applied for missing parameters to ensure reliable system performance.


## 4.6 System Integration and API Development

A backend API was developed to integrate the AI model, engineering calculations, and prompt-based input system.

The API was implemented using FastAPI and allows users to send input data either manually or as a natural language prompt.

<p align="center">
    <a href="images/Screenshot_2087.png">
        <img src="images/Screenshot_2087.png" alt="Testing the API-1" width="45%" />
    </a>
    <a href="images/Screenshot_2088.png">
        <img src="images/Screenshot_2088.png" alt="Testing the API-2" width="45%" />
    </a>
    <br/>
    <em>Figure 4.6a & 4.6b: Testing the API using natural language prompts</em>
</p>

The system processes the input, performs AI-based prediction, computes structural parameters, and returns the results in a structured format.


## 4.7 Flexible Prompt Interpretation     *

The system was enhanced to support flexible natural language input by allowing multiple representations of structural parameters.

For example:

Concrete strength can be entered as “fcu”, “fck”, “concrete grade”, or “grade of concrete”
Steel strength can be entered as “fy”, “steel grade”, or “grade of steel”

The system also supports different positional formats such as:

“6m span”
“span 6m”

This improves usability and allows the system to better interpret human language inputs.

<p align="center">
    <a href="images/Screenshot_2077.png">
        <img src="images/Screenshot_2077.png" alt="Flexible Prompt Interpretation" width="500" />
    </a>
    <br/>
    <em>Figure 4.7a: Flexible Prompt Interpretation</em>
</p>


## 4.8 Enhanced API Integration      *

The API was enhanced to support flexible user input by integrating an improved prompt parsing system.

The system allows different representations of structural parameters such as:

“fcu”, “fck”, and “concrete grade” for concrete strength
“fy”, “steel grade”, and “MPa” for steel strength

To maintain compatibility with the trained AI model, the extracted concrete strength (fcu) was internally mapped to fck before prediction.

This approach ensures both flexibility in user input and consistency in model performance.


## 4.9 Frontend Development

A user interface was developed using HTML, CSS, and JavaScript to allow interaction with the system.

The interface allows users to input design prompts and view computed structural results.

The frontend communicates with the backend API using HTTP requests and displays the results dynamically.

<p align="center">
    <a href="images/Screenshot_2089.png">
        <img src="images/Screenshot_2089.png" alt="Frontend interface" width="500" />
    </a>
    <br/>
    <em>Figure 4.9a: Frontend interface</em>
</p>


## 4.10 Graphical Visualization

Graphical representations of structural behavior were implemented to enhance system output.

Shear Force and Bending Moment diagrams were generated by computing values along the beam span and visualizing them using a charting library.

This allows users to better understand structural performance visually.

<p align="center">
    <a href="images/Screenshot_2090.png">
        <img src="images/Screenshot_2090.png" alt="Graphical visualization of shear and moment diagrams" width="500" />
    </a>
    <br/>
    <em>Figure 4.10a: Graphical visualization of shear and moment diagrams</em>
</p>


## 4.11 Load Representation and Wall Load Integration

The system was enhanced to include graphical representation of applied loads and additional structural loading conditions.

A load diagram was implemented to visualize the distribution of loads along the beam.

Furthermore, wall load calculations were integrated using the formula:

Wall Load = Density × Thickness × Height

The system automatically computes wall load when parameters are provided and adds it to the beam load to determine the total load acting on the structure.

This allows for a more comprehensive analysis of structural behavior under combined loading conditions.


## 4.12 Reinforcement Design Module

A reinforcement design module was implemented to convert the required steel area into practical reinforcement detailing.

Standard bar diameters were considered, and the number of bars required was computed based on the area of each bar.

The system selects the most efficient reinforcement option that satisfies the required steel area with minimal excess.

The reinforcement design recommendations are provided in the API response, allowing users to easily understand the required reinforcement for their beam design.

## 4.13 Model Validation

The AI-predicted steel area was compared with values obtained from conventional design equations.

This comparison was carried out to validate the accuracy of the model and ensure reliability of the system outputs.


---

## 4.14 Prompt Confirmation Modal

A confirmation modal was implemented to improve user experience and system transparency. When a user enters a natural language prompt and clicks "Generate Design", the system first parses the prompt and presents the extracted parameters in a modal dialog for user review before proceeding with the calculation.

The modal displays:

- Beam type (Simply Supported, Cantilever, Continuous, Overhang)
- Load type (UDL or Point Load)
- Load magnitude and material properties (fcu, fy)
- For continuous beams: span lengths and support types

This feature ensures that the system's interpretation of the input matches the user's intent, reducing errors in the design output.

<p align="center">
    <a href="images/modal_simple_beam.png">
        <img src="images/modal_simple_beam.png" alt="Prompt confirmation modal for simply supported beam" width="500" />
    </a>
    <br/>
    <em>Figure 4.14a: Prompt confirmation modal showing parsed parameters for a simply supported beam</em>
</p>

<p align="center">
    <a href="images/modal_continuous.png">
        <img src="images/modal_continuous.png" alt="Prompt confirmation modal for continuous beam" width="500" />
    </a>
    <br/>
    <em>Figure 4.14b: Prompt confirmation modal showing parsed parameters for a 3-span continuous beam with mixed support types (Fixed → Pinned → Roller → Pinned)</em>
</p>

The modal includes a "Confirm & Generate" button and a "Cancel" button, giving the user full control over the design process.


## 4.15 BS 8110 Bending Reinforcement Design

A comprehensive bending reinforcement design module was implemented following the BS 8110 code of practice for structural concrete design. This replaced the previous simplified steel area calculation with a rigorous, step-by-step procedure.

### 4.15.1 Design Procedure

The BS 8110 design procedure for singly reinforced beams follows these steps:

**Step 1: Effective Depth Calculation**

The effective depth is the distance from the compression face of the beam to the centroid of the tension reinforcement:

d = h − cover − link diameter − (bar diameter / 2)

Where:
- h = total beam depth (mm)
- cover = concrete cover to reinforcement (assumed 25mm)
- link = shear link diameter (assumed 8mm)
- bar = main reinforcement diameter (assumed 16mm initially)

**Step 2: Moment of Resistance**

The moment of resistance represents the maximum moment a singly reinforced section can resist:

M<sub>u</sub> = 0.156 × f<sub>cu</sub> × b × d²

Where:
- f<sub>cu</sub> = concrete cube strength (N/mm²)
- b = beam width (mm)
- d = effective depth (mm)

If the design moment M exceeds M<sub>u</sub>, the beam section is inadequate and must be increased.

**Step 3: K Constant**

K = M / (f<sub>cu</sub> × b × d²)

Note: K must not be greater than 0.156. If K > 0.156, the value 0.156 is used (singly reinforced section limit).

**Step 4: Lever Arm (z)**

z = d × [0.5 + √(0.25 − K/0.9)]

Note: z must not be greater than 0.95d. If z > 0.95d, the value 0.95d is used.

**Step 5: Required Area of Steel (A<sub>s</sub>)**

A<sub>s</sub> = M / (0.95 × f<sub>y</sub> × z)

Where:
- M = design moment (Nmm)
- f<sub>y</sub> = steel yield strength (N/mm²)
- z = lever arm (mm)

### 4.15.2 Implementation in the System

The design module (`design_bending_reinforcement` function) was implemented in `rules/beam_design.py` and accepts the following parameters:
- Design moment (kNm)
- Beam width and depth (mm)
- Concrete strength f<sub>cu</sub> (N/mm²)
- Steel yield strength f<sub>y</sub> (N/mm²)

The function returns the complete design breakdown including M<sub>u</sub>, K, z, A<sub>s</sub> required, and a section adequacy check.

<p align="center">
    <a href="images/bs8110_design_simple.png">
        <img src="images/bs8110_design_simple.png" alt="BS 8110 design results" width="500" />
    </a>
    <br/>
    <em>Figure 4.15a: BS 8110 bending design results displayed on the frontend, showing M<sub>u</sub>, d, K, z, A<sub>s</sub> required, A<sub>s</sub> provided, and section adequacy status</em>
</p>

<p align="center">
    <a href="images/bs8110_as_beam_diagram.png">
        <img src="images/bs8110_as_beam_diagram.png" alt="BS 8110 design results with beam diagram" width="500" />
    </a>
    <br/>
    <em>Figure 4.15b: BS 8110 design output showing K value, lever arm z, A<sub>s</sub> required and provided, along with the beam diagram for a simply supported beam</em>
</p>


## 4.16 Automatic Beam Size Estimation and Resizing

### 4.16.1 Standard Size Progressions

The system estimates beam sizes using standard width and depth progressions commonly used in practice:

**Width progression:** 230mm → 300mm → 450mm → 600mm → 750mm → 900mm
(First increase +70mm, then consistent +150mm)

**Depth progression:** 300mm → 450mm → 600mm → 750mm → 900mm → 1050mm → 1200mm
(Consistent increase of 150mm)

The minimum beam size is 230mm × 300mm.

### 4.16.2 Initial Size Selection

The initial beam size is selected based on the span-to-depth ratio deflection limits from BS 8110:

| Beam Type | Span/Depth Ratio Limit |
|---|---|
| Simply Supported | 20 |
| Cantilever | 7 |
| Continuous | 26 |
| Overhang | 20 |

The minimum depth is calculated as d<sub>min</sub> = Span × 1000 / Limit.

### 4.16.3 Automatic Resizing

If the design moment exceeds the moment of resistance (M > M<sub>u</sub>), the system automatically increases the beam section through the standard progressions until an adequate section is found. The resized beam is flagged in the output with a "(RESIZED)" label.

When a beam is resized, the system recalculates the beam self-weight and re-runs the entire design with the updated loads, ensuring consistency.


## 4.17 Factored Load Calculations (BS 8110)

The loading system follows BS 8110 partial safety factors:

**Design Load: n = 1.4G<sub>k</sub> + 1.6Q<sub>k</sub>**

Where:
- 1.4 = partial safety factor for dead/permanent loads (γ<sub>G</sub>)
- 1.6 = partial safety factor for live/imposed loads (γ<sub>Q</sub>)

The system calculates four load components:

**n1 — Slab Loading:** Provided by the user as UDL (kN/m)

**n2 — Beam Self-Weight:**
n2 = 1.4 × (width × depth × 24)
For example, a 230×300mm beam: 1.4 × (0.23 × 0.3 × 24) = 2.318 kN/m

**n3 — Wall Loading:**
n3 = 1.4 × (density × thickness × height)
For example, a 230mm wall of 2m height: 1.4 × (2.87 × 0.23 × 2) = 1.849 kN/m

**p1 — Point Load:** Calculated separately as it cannot be added to UDL

**w — Total UDL:** w = n1 + n2 + n3

<p align="center">
    <a href="images/results_simple_beam.png">
        <img src="images/results_simple_beam.png" alt="Load breakdown in the results panel" width="500" />
    </a>
    <br/>
    <em>Figure 4.17a: System output showing the complete load breakdown (n1, n2, n3, w, p1) for a simply supported beam under BS 8110</em>
</p>


## 4.18 Continuous Beam Analysis — Three-Moment Theorem

### 4.18.1 Background

For statically indeterminate structures such as continuous beams, the internal forces cannot be determined by equilibrium equations alone. The Three-Moment Theorem (Clapeyron's Theorem) was implemented as the analytical method for solving continuous beams with any number of spans.

### 4.18.2 Theoretical Basis

The Three-Moment Theorem relates the bending moments at three consecutive supports. For spans i and i+1 with lengths L<sub>i</sub> and L<sub>i+1</sub>:

M<sub>i-1</sub>·L<sub>i</sub> + 2·M<sub>i</sub>·(L<sub>i</sub> + L<sub>i+1</sub>) + M<sub>i+1</sub>·L<sub>i+1</sub> = −(6·A<sub>i</sub>·ā<sub>i</sub>/L<sub>i</sub> + 6·A<sub>i+1</sub>·b̄<sub>i+1</sub>/L<sub>i+1</sub>)

Where:
- M<sub>i-1</sub>, M<sub>i</sub>, M<sub>i+1</sub> = moments at supports i-1, i, i+1
- L<sub>i</sub>, L<sub>i+1</sub> = span lengths
- A<sub>i</sub> = area of free bending moment diagram for span i
- ā<sub>i</sub>, b̄<sub>i</sub> = centroid distances from left and right supports

### 4.18.3 Loading Terms

For a uniformly distributed load (UDL) w on a span of length L:
6Aā/L = 6Ab̄/L = wL³/4

For a point load P at distance a from the left support:
6Aā/L = Pa(L² − a²)/L
6Ab̄/L = Pb·a(2L − a)/L

### 4.18.4 Support Conditions

The solver supports three types of boundary conditions:

| Support Type | Condition | Symbol |
|---|---|---|
| Pinned | M = 0 at support | Triangle (▲) |
| Roller | M = 0 at support | Triangle on circle (▲○) |
| Fixed | M ≠ 0, solved via compatibility | Wall with hatching |

For fixed ends, additional equations are added to the system using the cantilever boundary condition: the fictitious span beyond the fixed end has zero length, generating an extra equation that determines the fixed-end moment.

### 4.18.5 Solution Process

1. Identify which support moments are unknowns (fixed ends) vs known zeros (pinned/roller)
2. Build a system of linear equations from the Three-Moment equations
3. Solve using matrix algebra (numpy linear solver)
4. Compute reactions using per-span equilibrium
5. Generate shear force and bending moment diagrams for each span

The solver is implemented in `rules/continuous_beam.py` using the `solve_three_moment()` function.

<p align="center">
    <a href="images/continuous_analysis.png">
        <img src="images/continuous_analysis.png" alt="Continuous beam analysis results" width="500" />
    </a>
    <br/>
    <em>Figure 4.18a: Continuous beam analysis results showing support moments (M<sub>A</sub> through M<sub>D</sub>) and support reactions (R<sub>A</sub> through R<sub>D</sub>) computed using the Three-Moment Theorem</em>
</p>


## 4.19 Per-Location Reinforcement Design for Continuous Beams

### 4.19.1 Design Philosophy

Unlike simply supported beams where there is typically a single critical section, continuous beams have multiple critical sections:

- **At supports (hogging moments):** The beam experiences negative (hogging) bending moments at interior supports, requiring top steel reinforcement.
- **At mid-spans (sagging moments):** The beam experiences positive (sagging) bending moments within each span, requiring bottom steel reinforcement.

Each of these locations must be individually designed to determine the required area of steel.

### 4.19.2 Implementation

The system performs the BS 8110 design procedure (K → z → A<sub>s</sub>) at every critical location:

**Support Design (Hogging):**
- Uses the support moment from the Three-Moment solution
- Designs top reinforcement at each interior support
- Supports with M = 0 (pinned/roller at beam ends) require no reinforcement

**Span Design (Sagging):**
- Extracts the maximum positive (sagging) moment from the moment diagram within each span
- Designs bottom reinforcement for each span

The governing (largest A<sub>s</sub>) determines the overall reinforcement recommendation.

### 4.19.3 Reinforcement Design Table

The frontend displays a color-coded table showing the design at each location:

- **Red rows** = hogging moments at supports (top steel)
- **Green rows** = sagging moments at mid-spans (bottom steel)

Each row shows: Location, Type, M (kNm), K, z (mm), A<sub>s</sub> required (mm²), and Reinforcement selection.

<p align="center">
    <a href="images/reinf_table.png">
        <img src="images/reinf_table.png" alt="Per-location reinforcement design table" width="500" />
    </a>
    <br/>
    <em>Figure 4.19a: Per-location reinforcement design table for a 3-span continuous beam, showing hogging reinforcement at supports (red) and sagging reinforcement at spans (green), with K, z, A<sub>s</sub> calculations for each location</em>
</p>

### 4.19.4 Deflection Check

For continuous beams, the deflection check uses the span with the largest sagging moment (the critical span). The span-to-depth ratio for continuous beams is limited to 26 as per BS 8110.


## 4.20 Support Type Visualization

### 4.20.1 Standard Engineering Symbols

The beam diagram visualization was enhanced to display three distinct support types using standard structural engineering symbols:

| Support Type | Symbol Description | Color |
|---|---|---|
| **Fixed** | Vertical wall with diagonal hatching lines | Red (#ef4444) |
| **Pinned** | Inverted triangle with ground line and hatching | Green (#10b981) |
| **Roller** | Inverted triangle resting on a circle with ground line | Amber (#f59e0b) |

These symbols follow conventional structural engineering drawing conventions and are rendered using HTML5 Canvas.

### 4.20.2 Multi-Span Beam Diagram

For continuous beams, the diagram includes:
- Beam line spanning across all supports
- Support symbols at each support location with labels (A, B, C, D...)
- Span length labels between supports
- Support moment values displayed above each support

<p align="center">
    <a href="images/beam_diagram_continuous.png">
        <img src="images/beam_diagram_continuous.png" alt="Multi-span beam diagram with different support types" width="500" />
    </a>
    <br/>
    <em>Figure 4.20a: Multi-span continuous beam diagram showing fixed support at A (red), pinned at B and D (green), and roller at C (amber), with span lengths and support moments labeled</em>
</p>

<p align="center">
    <a href="images/beam_diagram_simple.png">
        <img src="images/beam_diagram_simple.png" alt="Simply supported beam diagram" width="500" />
    </a>
    <br/>
    <em>Figure 4.20b: Simply supported beam diagram showing pinned (left) and roller (right) supports with UDL representation</em>
</p>


## 4.21 Graphical Visualization of Structural Behavior

### 4.21.1 Diagrams Generated

The system generates three diagrams for every beam analysis:

1. **Load Diagram:** Shows the distribution of applied loads along the beam span
2. **Shear Force Diagram (SFD):** Shows how the internal shear force varies along the beam
3. **Bending Moment Diagram (BMD):** Shows how the internal bending moment varies along the beam

For continuous beams, these diagrams are stitched together from per-span data to create a single continuous visualization across all spans.

### 4.21.2 Peak Value Annotation

The bending moment diagram automatically identifies and annotates the peak moment location, showing both the moment value and its position along the beam.

<p align="center">
    <a href="images/graphs_simple_beam.png">
        <img src="images/graphs_simple_beam.png" alt="SFD and BMD for simply supported beam" width="500" />
    </a>
    <br/>
    <em>Figure 4.21a: Shear Force and Bending Moment diagrams for a simply supported beam under UDL, with peak moment annotation</em>
</p>

<p align="center">
    <a href="images/graphs_continuous.png">
        <img src="images/graphs_continuous.png" alt="SFD and BMD for continuous beam" width="500" />
    </a>
    <br/>
    <em>Figure 4.21b: Shear Force and Bending Moment diagrams for a 3-span continuous beam, showing the variation of forces across all spans</em>
</p>


## 4.22 System Architecture Summary

### 4.22.1 Module Structure

The complete system consists of the following modules:

| Module | File | Purpose |
|---|---|---|
| NLP Parser | `nlp/prompt_parser.py` | Extracts structural parameters from natural language input |
| Beam Design | `rules/beam_design.py` | BS 8110 design calculations, load factors, reinforcement |
| Continuous Beam | `rules/continuous_beam.py` | Three-Moment Theorem solver for multi-span beams |
| API | `api/main.py` | FastAPI backend routing, integration of all modules |
| Report | `api/report.py` | PDF report generation |
| Frontend | `api/static/` | HTML, CSS, JavaScript user interface |
| AI Model | `model.pkl` | Machine learning model for steel area prediction |

### 4.22.2 Data Flow

The system operates through the following data flow:

1. **User Input** → Natural language prompt entered in the frontend
2. **Parsing** → `prompt_parser.py` extracts span, load, beam type, support types
3. **Confirmation** → Modal displays parsed parameters for user review
4. **API Routing** → `main.py` routes to appropriate solver (single-span or continuous)
5. **BS 8110 Design** → Factored loads → Design moments → K → z → A<sub>s</sub>
6. **Reinforcement** → Area of steel → Bar selection (diameter & number)
7. **Diagrams** → SFD, BMD, Load diagrams generated
8. **Frontend Display** → Results, design breakdown, diagrams, and beam visualization

### 4.22.3 Supported Beam Types

| Beam Type | Analysis Method | Key Features |
|---|---|---|
| Simply Supported | Static equilibrium | UDL and point loads |
| Cantilever | Static equilibrium | Fixed end, free end |
| Overhang | Static equilibrium | Extension beyond support |
| Continuous (2+ spans) | Three-Moment Theorem | Any number of spans, mixed supports |

### 4.22.4 Supported Support Types

| Type | Structural Behavior | Moment Condition |
|---|---|---|
| Pinned | Allows rotation, prevents translation | M = 0 |
| Roller | Allows rotation and horizontal translation | M = 0 |
| Fixed | Prevents rotation and translation | M ≠ 0 (solved) |

### 4.22.5 Test Validation Results

The system was validated using three test cases:

**Test 1: Simply Supported Beam (6m span, 20 kN/m UDL)**
- Beam size: 230mm × 450mm (resized from 300mm depth)
- M = 100.43 kNm, M<sub>u</sub> = 150.05 kNm (adequate)
- K = 0.10441, z = 354.21 mm
- A<sub>s</sub> required = 648.81 mm², Provided = 678.58 mm² (6Y12)
- Deflection: SAFE

**Test 2: 3-Span Continuous Beam (8m + 6m + 4m, 20 kN/m UDL)**
- Supports: Fixed → Pinned → Roller → Pinned
- Governing moment: 136.53 kNm at Support A (hogging)
- K = 0.14194, z = 328.75 mm
- A<sub>s</sub> required = 950.37 mm², Provided = 981.75 mm² (2Y25)
- Per-location design: 6 critical sections designed individually

**Test 3: 2-Span Continuous Beam (6m + 5m, 15 kN/m UDL, fixed both ends)**
- Beam size: 230mm × 300mm
- M<sub>u</sub> = 60.17 kNm (adequate)
- All support and span reinforcement designed individually

All test results verified equilibrium (ΣReactions = Total Applied Load) and section adequacy checks.


## 4.23 Automatic UI Reset on New Design Generation

### 4.23.1 Problem

When a user generates a design and then enters a new prompt without refreshing the page, stale data from the previous design (results, graphs, beam diagrams) would remain visible and could overlap with or be confused for the new results. Chart.js instances would also accumulate in memory, potentially causing rendering glitches.

### 4.23.2 Solution

An automatic reset mechanism (`resetUI()`) was implemented that executes at the start of every new design generation. When the user clicks "Confirm & Generate" in the modal, the system clears all cached data before the new API call is made.

### 4.23.3 What is Cleared

The reset function performs the following actions:

| Component | Action |
|---|---|
| **Result text fields** | All span elements (beam type, load values, moments, shear, steel area, reinforcement, beam size, deflection) are cleared to empty strings |
| **BS 8110 Design section** | The `designData` container is emptied and hidden |
| **Continuous Beam section** | The `continuousData` container (support moments, reactions, reinforcement table) is emptied and hidden |
| **Chart.js graphs** | All three chart instances (Load, Shear Force, Bending Moment diagrams) are destroyed to free memory and prevent overlay issues |
| **Beam diagram canvas** | The HTML5 Canvas is cleared using `clearRect()` to remove the previous beam visualization |

### 4.23.4 Implementation

The `resetUI()` function is called as the first action inside the `generate()` function, before the loading spinner appears and before the API request is sent. This ensures the user sees a clean interface while the new design is being computed.

This approach guarantees that:

1. No stale data from a previous design is ever displayed alongside new results
2. Chart.js instances are properly destroyed, preventing memory leaks
3. The beam diagram canvas is cleared, preventing old support symbols from persisting
4. The transition between consecutive designs is smooth and unambiguous


## 4.24 BS 8110 Deflection Check (Table 3.9)

### 4.24.1 Overview

The deflection check was upgraded from a simple span-to-depth ratio comparison to a comprehensive BS 8110 compliant procedure using Table 3.9 basic ratios, service stress, and modification factors.

The previous deflection check only compared the beam depth against a basic span/depth limit. The new implementation follows the complete BS 8110 procedure:

1. Determine the **basic span/effective depth ratio** from Table 3.9
2. Calculate the **service stress** (f<sub>s</sub>)
3. Compute the **modification factor** (MF)
4. Compare the **actual span/d ratio** against the **allowable ratio** (basic × MF)

### 4.24.2 Table 3.9 — Basic Span/Effective Depth Ratios

| Support Condition | Basic Ratio |
|---|---|
| Cantilever | 7 |
| Simply Supported | 20 |
| Continuous | 26 |

### 4.24.3 Service Stress (f<sub>s</sub>)

The service stress in the tension reinforcement is calculated as:

f<sub>s</sub> = (2/3) × f<sub>y</sub> × (A<sub>s,req</sub> / A<sub>s,prov</sub>) × (1/β<sub>b</sub>)

Where:
- f<sub>y</sub> = characteristic strength of steel reinforcement (N/mm²)
- A<sub>s,req</sub> = required area of steel (mm²)
- A<sub>s,prov</sub> = provided area of steel (mm²)
- β<sub>b</sub> = ratio of redistributed moment to elastic moment (default 1.0)

### 4.24.4 Modification Factor (MF)

The modification factor accounts for the tension reinforcement provided:

MF = 0.55 + (477 − f<sub>s</sub>) / [120 × (0.9 + M/bd²)]

Where:
- f<sub>s</sub> = service stress (N/mm²)
- M = design moment (Nmm)
- b = beam width (mm)
- d = effective depth (mm)

**Note:** MF must not be greater than 2.0. If the calculated value exceeds 2.0, the value 2.0 is used.

### 4.24.5 Deflection Adequacy

The deflection check compares:

- **Actual span/d ratio** = (span × 1000) / d
- **Allowable span/d ratio** = basic ratio × MF

If actual ≤ allowable → **SAFE** (deflection is adequate)
If actual > allowable → **NOT SAFE** (deflection fails)

### 4.24.6 Automatic Correction

If the deflection check fails, the system automatically attempts corrections in the following order:

1. **Increase A<sub>s,prov</sub>:** Try larger bar diameter or more bars to reduce the service stress f<sub>s</sub>, which increases the modification factor MF, thereby increasing the allowable span/d ratio.

2. **Increase beam depth:** If increasing the reinforcement alone cannot satisfy the deflection check, the system increases the beam depth to the next standard size and recalculates the entire design (new d → new K → new z → new A<sub>s</sub> → new deflection check).

The system iterates through these options until a satisfactory design is found, and flags any adjustments in the output.

<p align="center">
    <a href="images/deflection_check.png">
        <img src="images/deflection_check.png" alt="BS 8110 deflection check results" width="500" />
    </a>
    <br/>
    <em>Figure 4.24a: BS 8110 deflection check output showing basic span/d ratio (Table 3.9), service stress f<sub>s</sub>, modification factor MF, allowable vs actual span/d ratio, and the final status</em>
</p>

### 4.24.7 Test Validation

The deflection check was validated across three beam types:

| Beam Type | Span | Basic Ratio | f<sub>s</sub> (N/mm²) | MF | Allowable span/d | Actual span/d | Status |
|---|---|---|---|---|---|---|---|
| Simply Supported | 6m | 20 | 293.21 | 0.9863 | 19.73 | 14.67 | SAFE |
| Continuous (major span) | 8m | 26 | 284.73 | 1.1474 | 29.83 | 19.56 | SAFE |
| Cantilever | 3m | 7 | 290.80 | 1.0569 | 7.40 | 7.33 | SAFE |

All test cases passed the BS 8110 deflection check with proper service stress and modification factor calculations.


## 4.25 Enhanced Continuous Beam Diagram Visualization

### 4.25.1 UDL Load Arrows on Continuous Beams

The continuous beam diagram was enhanced to include uniformly distributed load (UDL) arrows pointing downward across all spans. Previously, only single-span beams displayed load arrows; continuous beam diagrams only showed the beam line, supports, and labels.

The enhanced diagram now displays:

- A horizontal top line connecting all arrow starting points
- Downward-pointing arrows at regular intervals across the entire beam length (~2 arrows per metre)
- Arrow heads at the bottom of each vertical line to indicate load direction
- A load value label (e.g., "20 kN/m") centered above the arrows

This visual representation follows standard structural engineering drawing conventions and makes the loading condition immediately clear.

### 4.25.2 Complete Diagram Elements

The updated continuous beam diagram includes all of the following elements:

| Element | Position | Description |
|---|---|---|
| **Support moment values** | Top (red) | M=−136.5, M=−102.6, M=−51.4 |
| **Span length labels** | Above arrows (amber) | 8m, 6m, 4m |
| **UDL load label** | Above arrows (green) | 20 kN/m |
| **UDL arrows** | Between label and beam | Downward arrows across all spans |
| **Beam line** | Centre (blue) | Horizontal line spanning all supports |
| **Support symbols** | Below beam | Fixed (red), Pinned (green), Roller (amber) |
| **Support labels** | Below symbols (green) | A, B, C, D |

<p align="center">
    <a href="images/continuous_udl_diagram.png">
        <img src="images/continuous_udl_diagram.png" alt="Continuous beam diagram with UDL arrows" width="500" />
    </a>
    <br/>
    <em>Figure 4.25a: Enhanced continuous beam diagram showing UDL load arrows pointing downward across all spans, with support moments, span labels, and mixed support types</em>
</p>


## 4.26 Per-Span Load Type Rendering for Continuous Beams

### 4.26.1 Overview

The continuous beam diagram was further enhanced to render load arrows based on the **actual load type of each span**, rather than always displaying UDL arrows across the entire beam. Each span now independently shows its correct load representation.

### 4.26.2 Load Type Visual Conventions

| Load Type | Colour | Visual Representation |
|---|---|---|
| **UDL** (Uniformly Distributed Load) | Green (#10b981) | Multiple evenly-spaced downward arrows connected by a horizontal top line, with load value in kN/m |
| **Point Load** | Red (#ef4444) | Single bold downward arrow at the load position, with load value in kN |

### 4.26.3 Data Flow

The API response now includes a `span_loads` array in the `continuous` object. Each entry describes the load on one span:

**UDL span:**
```json
{ "type": "udl", "w": 23.478 }
```

**Point load span:**
```json
{ "type": "point_load", "P": 50.0, "a": 3.0 }
```

Where:
- `w` = factored UDL intensity (kN/m)
- `P` = point load magnitude (kN)
- `a` = distance from the left support of the span to the point load (m)

### 4.26.4 Rendering Logic

The `drawContinuousBeamDiagram()` function iterates through each span and checks its load type:

1. **UDL spans:** Draws a per-span set of downward arrows with a connecting top line and displays the load intensity (kN/m) above each span independently.

2. **Point load spans:** Draws a single bold arrow at the exact load position within the span, with the load magnitude (kN) labelled above. The arrow position is calculated proportionally: `px = spanStart + (a / spanLength) × spanPixels`.

This approach supports mixed loading scenarios where different spans on the same continuous beam may carry different load types.


## 4.27 BS 8110 Shear Reinforcement Design (Stirrups/Links)

### 4.27.1 Overview

A complete shear reinforcement design module was implemented in accordance with BS 8110 Clause 3.4.5. The system now automatically designs stirrups (links) for both single-span and continuous beams based on the calculated ultimate shear force.

The design process follows four key steps:
1. Calculate the **shear stress** (v)
2. Check against the **ultimate shear limit** (v<sub>max</sub>)
3. Determine the **concrete shear capacity** (v<sub>c</sub>)
4. Select the appropriate **stirrup diameter and spacing**

### 4.27.2 Shear Stress

The design shear stress is calculated as:

v = V / (b × d)

Where:
- V = ultimate shear force (N)
- b = beam width (mm)
- d = effective depth (mm)

### 4.27.3 Ultimate Shear Limit

The shear stress must not exceed the ultimate limit:

v<sub>max</sub> = min(0.8√f<sub>cu</sub>, 5.0) N/mm²

If v > v<sub>max</sub>, the beam section is inadequate and must be increased.

### 4.27.4 Concrete Shear Capacity (Table 3.8)

The concrete shear capacity v<sub>c</sub> is calculated using:

v<sub>c</sub> = 0.79 × (100A<sub>s</sub>/bd)<sup>1/3</sup> × (400/d)<sup>1/4</sup> × (f<sub>cu</sub>/25)<sup>1/3</sup> / γ<sub>m</sub>

Where:
- 100A<sub>s</sub>/bd is capped at 3.0
- (400/d)<sup>1/4</sup> is not less than 0.67
- f<sub>cu</sub> is capped at 40 N/mm²
- γ<sub>m</sub> = 1.25 (partial safety factor)

### 4.27.5 Shear Reinforcement Cases

| Condition | Link Type | A<sub>sv</sub>/s<sub>v</sub> Required |
|---|---|---|
| v < 0.5v<sub>c</sub> | Nominal links | 0.4b / (0.87f<sub>yv</sub>) |
| 0.5v<sub>c</sub> ≤ v ≤ v<sub>c</sub> + 0.4 | Minimum links | 0.4b / (0.87f<sub>yv</sub>) |
| v > v<sub>c</sub> + 0.4 | Design links | b(v − v<sub>c</sub>) / (0.87f<sub>yv</sub>) |

### 4.27.6 Stirrup Selection

Two-legged stirrups are used. The system selects from standard link diameters (Y8, Y10, Y12) and calculates the required spacing:

s<sub>v</sub> = A<sub>sv</sub> / (A<sub>sv</sub>/s<sub>v</sub> required)

Where A<sub>sv</sub> = 2 × (π/4) × d<sub>link</sub>²

The spacing is:
- Rounded down to the nearest 25mm
- Capped at 0.75d (BS 8110 Clause 3.4.5.5)
- Not less than 50mm

### 4.27.7 Test Validation

The shear design was validated across three beam types:

| Beam Type | V (kN) | v (N/mm²) | v<sub>c</sub> (N/mm²) | Link Type | Stirrups |
|---|---|---|---|---|---|
| Simply Supported | 60 | 0.64 | 0.56 | Minimum | Y8 @ 300mm c/c |
| Continuous | 120 | 1.28 | 0.64 | Design | Y8 @ 250mm c/c |
| Cantilever | 45 | 0.48 | 0.53 | Minimum | Y8 @ 300mm c/c |

### 4.27.8 Implementation Files

| File | Function | Purpose |
|---|---|---|
| `rules/beam_design.py` | `concrete_shear_capacity()` | Calculates v<sub>c</sub> per Table 3.8 |
| `rules/beam_design.py` | `design_shear_reinforcement()` | Complete shear design with link selection |
| `rules/beam_design.py` | `_select_links()` | Stirrup diameter and spacing selection |
| `api/main.py` | Single-span & continuous paths | Integrates shear design into API response |
| `api/static/script.js` | Design results section | Displays full shear breakdown in UI |


## 4.28 PDF Download Modal System

### 4.28.1 Overview

The single "Download PDF" button was replaced with a modal-based download system that offers two distinct document types:

1. **Download Results** — A comprehensive PDF report containing all design outputs
2. **Download Calculation Sheet** — Reserved for future implementation (placeholder)

### 4.28.2 User Interface

When the user clicks "Download PDF", a modal overlay appears with the following options:

| Button | Colour | Action |
|---|---|---|
| 📄 Download Results | Green (gradient) | Generates and downloads a full results PDF |
| 📋 Download Calculation Sheet | Purple (gradient) | Displays "not yet available" message |
| Cancel | Neutral outline | Closes the modal |

The modal reuses the existing `.modal-overlay` / `.modal-box` CSS pattern established by the parameter confirmation modal.

<p align="center">
    <a href="images/Screenshot_2168.png">
        <img src="images/Screenshot_2168.png" alt="PDF Modal Options" width="500" />
    </a>
    <br/>
    <em>Figure 4.28a: PDF Modal Options for downloading the results and calculation sheet</em>
</p>

### 4.28.3 Data Flow

The frontend stores the complete API response (`lastDesignData`) when a design is generated. When the user clicks "Download Results":

1. The stored data is sent directly to `/download-report` via POST
2. The backend generates a PDF using ReportLab
3. The PDF is returned as a file download

This eliminates the need to re-run the design calculation, ensuring the PDF matches exactly what is shown on screen.

### 4.28.4 PDF Report Contents

The results PDF includes all sections relevant to the beam type:

| Section | Content | Applicable To |
|---|---|---|
| 1. Input Parameters | Beam type, load, span, supports, material grades | All |
| 2. Beam Size | Width × depth, resize indicator | All |
| 3. Load Breakdown | n1, n2, n3, w, p1 | All |
| 4. Design Results | M, V, As required/provided, reinforcement | All |
| 5. BS 8110 Bending Design | Mu, d, K, z, adequacy status | All |
| 6. Deflection Check | Basic ratio, fs, MF, allowable vs actual | All |
| 7. Shear Design | v, v_max, vc, link type, stirrup details | All |
| 8. Continuous Analysis | Support moments, reactions, per-location reinforcement table | Continuous only |

### 4.28.5 API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/download-report` | POST | Generates comprehensive results PDF from full design data |
| `/download-calculation-sheet` | POST | Placeholder — returns 501 Not Implemented |

### 4.28.6 Implementation Files

| File | Change |
|---|---|
| `api/static/index.html` | Added download modal HTML with two buttons |
| `api/static/script.js` | Added `openDownloadModal()`, `closeDownloadModal()`, `downloadResults()`, `downloadCalculationSheet()`, and `lastDesignData` storage |
| `api/report.py` | Completely rewritten to generate a comprehensive PDF for all beam types |
| `api/main.py` | Updated `/download-report` to accept full data directly; added `/download-calculation-sheet` placeholder |


## 4.29 Diagram Embedding in PDF Results Report

### 4.29.1 Overview

The PDF results report was enhanced to include all four visual diagrams rendered on the frontend. When the user clicks "Download Results", the system captures the current state of all diagram canvases, encodes them as base64 PNG images, and sends them alongside the design data to the backend, where they are decoded and embedded into the PDF.

### 4.29.2 Captured Diagrams

| Canvas ID | Diagram Name | Source |
|---|---|---|
| `beamCanvas` | Beam Diagram | Custom HTML5 Canvas drawing (supports, loads, dimensions) |
| `loadChart` | Load Diagram | Chart.js — load distribution along the beam |
| `shearChart` | Shear Force Diagram | Chart.js — V(x) curve |
| `momentChart` | Bending Moment Diagram | Chart.js — M(x) curve |

### 4.29.3 Data Flow

```
Frontend Canvas → toDataURL("image/png") → base64 string
    ↓
payload.diagrams_base64 = { beam_diagram, load_diagram, shear_diagram, moment_diagram }
    ↓
POST /download-report (JSON payload with base64 images)
    ↓
Backend: base64.b64decode → io.BytesIO → ReportLab Image → PDF
```

### 4.29.4 Frontend Implementation

In `downloadResults()`, before sending the fetch request:

1. The `beamCanvas` element is captured via `canvas.toDataURL("image/png")`
2. The three Chart.js canvases (`loadChart`, `shearChart`, `momentChart`) are captured similarly
3. All base64 strings are attached to the payload under `diagrams_base64`

### 4.29.5 Backend Implementation

In `report.py`, a new Section 9 was added:

1. The `diagrams_base64` dictionary is extracted from the incoming data
2. Each base64 string is stripped of the `data:image/png;base64,` prefix
3. The raw bytes are decoded and wrapped in a `BytesIO` buffer
4. The image's actual pixel dimensions are read via `ImageReader.getSize()` to determine the natural aspect ratio
5. ReportLab's `Image` flowable is used to embed each diagram, scaled to fit the A4 page width while preserving its original aspect ratio
6. Each diagram is labelled with its title (Beam Diagram, Load Diagram, Shear Force Diagram, Bending Moment Diagram)

### 4.29.6 PDF Output

The diagrams section appears as **Section 9** in the PDF, after the continuous beam analysis (if applicable) and before the footer. Each diagram is:
- Centred on the page
- Scaled proportionally to fit the available page width (A4 minus margins)
- Maintains its original canvas aspect ratio so that axis labels, tick numbers, and chart text remain fully readable
- Labelled with a descriptive title

### 4.29.7 Implementation Files

| File | Change |
|---|---|
| `api/static/script.js` | Added canvas capture logic in `downloadResults()` using `toDataURL()` |
| `api/report.py` | Added base64 decoding, `Image` import, and Section 9 diagram rendering |


## 4.30 Beam Diagram Visual Improvements

### 4.30.1 Unified Colour Scheme

All beam type diagrams (simply supported, cantilever, overhang) were updated to use the same colour palette as the continuous beam diagram, replacing the previous white-only rendering.

| Element | Colour | Hex Code |
|---|---|---|
| Beam line | Blue | `#3b82f6` |
| Pinned support | Green | `#10b981` |
| Roller support | Amber | `#f59e0b` |
| Fixed support | Red | `#ef4444` |
| Span labels | Amber (bold) | `#f59e0b` |
| Support labels (A, B, C) | Green (bold) | `#10b981` |
| UDL arrows & labels | Green | `#10b981` |

The `drawSupport()` function now applies per-type colouring, matching the separate `drawPinnedSupport()`, `drawRollerSupport()`, and `drawFixedSupport()` functions used by the continuous beam diagram.

### 4.30.2 Continuous Beam Dimension Tick Marks

The span dimension lines in the continuous beam diagram were enhanced with vertical tick marks at each boundary:

- **Left tick**: Drawn at the start of each span's dashed line
- **Right tick**: Drawn at the end of each span's dashed line
- **Tick height**: 5px above and below the dimension line centre

This makes span boundaries clearly demarcated, especially where adjacent spans share a support point.

### 4.30.3 PDF Chart Diagram Improvements

Two improvements were made to the Chart.js diagrams embedded in the PDF results report:

1. **Dark Background**: Each Chart.js diagram (load, shear, moment) is composited onto a dark background (`#1e293b`) using Pillow before embedding. This ensures the white axis labels, tick numbers, and chart text remain fully visible on the white PDF page.

2. **Spacing**: Diagram spacing was increased to 14pt between charts, providing comfortable visual separation while still fitting all three on a single A4 page.

### 4.30.4 Implementation Files

| File | Change |
|---|---|
| `api/static/script.js` | Updated `drawBeamDiagram()`, `drawSupport()` with coloured elements; added vertical ticks to `drawContinuousBeamDiagram()` |
| `api/report.py` | Added Pillow-based dark background compositing; increased chart spacing to 14pt |


## 4.31 Beam Design Calculation Sheet (Download Calculation Sheet)

### 4.31.1 Overview

A comprehensive **Beam Design Calculation Sheet** PDF was implemented, modelled after professional structural engineering software output (e.g., Orion Building Design System). When the user clicks **"Download Calculation Sheet"** from the download modal, the system generates a detailed, multi-section PDF containing all BS 8110 design calculations, embedded diagrams, and a reinforcement schedule.

This replaces the previous `501 Not Implemented` placeholder on the `/download-calculation-sheet` endpoint.

### 4.31.2 PDF Layout Structure

The calculation sheet contains 8 sections:

| Section | Content |
|---|---|
| 1. Header | System name, beam type, material grades (C_fcu_/Grade fy), load type |
| 2. Beam Geometry | Beam size (b × h), span(s), support types, material properties |
| 3. Load Breakdown | n1 (slab load), n2 (self-weight), n3 (wall load), p1 (point load), w (total UDL) |
| 4. Diagrams | Beam diagram, Load diagram, Shear Force Diagram, Bending Moment Diagram |
| 5. Bending Design | Full BS 8110 bending design — M, Mu, d, K, K', z, As_req, As_prov, bars |
| 6. Shear Design | V, v, v_max, v_c, link type, stirrups description, status |
| 7. Deflection Check | Basic span/d, fs, MF, allowable vs actual span/d, pass/fail |
| 8. Reinforcement Schedule | Per-location bar schedule with As_req vs As_prov and OK/FAIL status |

### 4.31.3 Beam Type Support

| Beam Type | Bending Table | Reinforcement Schedule |
|---|---|---|
| Simply Supported | Single-section table (Parameter → Symbol → Value → Unit) | Main bars (bottom) + nominal top bars |
| Cantilever | Same single-section format | Same |
| Overhang | Same single-section format | Same |
| Continuous | **Per-location tables**: Top Edge (hogging at supports) + Bottom Edge (sagging at spans) + Support Moments & Reactions summary | Per-location schedule with top/bottom bars at each support/span |

### 4.31.4 Data Flow

```
Frontend: Generate Design → lastDesignData stored
    ↓
User clicks "Download Calculation Sheet"
    ↓
downloadCalculationSheet() captures canvas diagrams as base64 PNG
    ↓
POST /download-calculation-sheet (full design data + diagrams_base64)
    ↓
api/calc_sheet.py → generate_calc_sheet(data) → ReportLab PDF
    ↓
FileResponse → browser downloads "ai_beam_calc_sheet.pdf"
```

### 4.31.5 Visual Design

The calculation sheet uses a professional colour palette:
- **Header**: Dark navy background (`#1e3a5f`) with white text
- **Section headers**: Slate grey background (`#cdd5e0`) with bold text
- **Row labels**: Light grey background (`#e8ecf1`) for parameter names
- **Grid**: Subtle grey borders (`#94a3b8`)
- **Pass/Fail**: Green (`#15803d`) for OK, red (`#dc2626`) for FAIL
- **Chart diagrams**: Dark background compositing (`#1e293b`) for readable white chart text

### 4.31.6 Implementation Files

| File | Change |
|---|---|
| `api/calc_sheet.py` | **New file** — Complete calculation sheet PDF generator with 8 sections |
| `api/main.py` | Updated `/download-calculation-sheet` endpoint; added `generate_calc_sheet` import |
| `api/static/script.js` | Updated `downloadCalculationSheet()` to send full data payload with diagram captures and proper DOM-based file download |
| `api/static/index.html` | Cache bust to v17 |


## 4.32 Custom Project Title Integration

A custom project title feature was integrated to allow users to personalize the generated calculation sheets. 
When the user clicks the "Download PDF" button, a modal prompts them for an optional "Project Title". If provided, this title is injected into the PDF generation payload and elegantly embedded at the top of the Calculation Sheet using a distinguished font colour (`#1e3a5f`), providing professional branding for specific engineering projects.


## 4.33 Factored Wall Loading Update (BS 8110)

The wall loading algorithm was corrected to adhere to standard structural engineering practices. Previously, a raw value (e.g. 2.87) was treated as density. Following engineering review, this was revised to calculate the precise **Wall Line Load** in kN/m using the formula:

`Wall Line Load = Unit Weight × Thickness × Height`

The system now enforces a default unit weight of 20.0 kN/m³ (representing conventional hollow block masonry) unless the user specifically overrides it in the prompt. The resulting Wall Line Load is then factored using the BS 8110 permanent load safety factor (1.4):

`n3 = 1.4 × Wall Line Load`

This corrected calculation is now dynamically presented in both the user interface and the exported PDF calculation sheet load breakdown.


## 4.34 Overhang Beam Handling Improvements

Several issues affecting the presentation of Overhang beams were resolved:

1. **Robust Prompt Parsing**: The natural language parser (`nlp/prompt_parser.py`) was enhanced to recognize diverse overhang definitions in prompts (e.g. `overhang 2m`, `overhang of 2.5m`, `overhang: 2m`, `overhang = 2m`).
2. **Distinct Geometry Display**: The user interface (Results panel) and the generated PDF reports were modified. Previously, the "Span" label was used generically. Now, when an overhang beam is detected, the system distinctly breaks down the total length, explicitly displaying both the main **Span** and the **Overhang Length**.
3. **Diagram Integrity**: The Canvas beam diagram was updated to proportionally render the overhang segment when specified, preventing UI bugs where a zero or undetected overhang defaulted to a standard span rendering.


## 4.35 Enhanced System Branding & UI

### 4.35.1 AI-RCBDS Nomenclature
The system's name was officially updated to **AI-RCBDS (AI Reinforced Concrete Beam Design System)**. The PDF report headers, the calculation sheet titles, and the downloaded PDF filenames were all updated to reflect this new identity (e.g., `ai-rcbds_calc_sheet.pdf` and `ai-rcbds_results_report.pdf`).

### 4.35.2 Landing Page Overlay
| `momentChart` | Bending Moment Diagram | Chart.js — M(x) curve |

### 4.29.3 Data Flow

```
Frontend Canvas → toDataURL("image/png") → base64 string
    ↓
payload.diagrams_base64 = { beam_diagram, load_diagram, shear_diagram, moment_diagram }
    ↓
POST /download-report (JSON payload with base64 images)
    ↓
Backend: base64.b64decode → io.BytesIO → ReportLab Image → PDF
```

### 4.29.4 Frontend Implementation

In `downloadResults()`, before sending the fetch request:

1. The `beamCanvas` element is captured via `canvas.toDataURL("image/png")`
2. The three Chart.js canvases (`loadChart`, `shearChart`, `momentChart`) are captured similarly
3. All base64 strings are attached to the payload under `diagrams_base64`

### 4.29.5 Backend Implementation

In `report.py`, a new Section 9 was added:

1. The `diagrams_base64` dictionary is extracted from the incoming data
2. Each base64 string is stripped of the `data:image/png;base64,` prefix
3. The raw bytes are decoded and wrapped in a `BytesIO` buffer
4. The image's actual pixel dimensions are read via `ImageReader.getSize()` to determine the natural aspect ratio
5. ReportLab's `Image` flowable is used to embed each diagram, scaled to fit the A4 page width while preserving its original aspect ratio
6. Each diagram is labelled with its title (Beam Diagram, Load Diagram, Shear Force Diagram, Bending Moment Diagram)

### 4.29.6 PDF Output

The diagrams section appears as **Section 9** in the PDF, after the continuous beam analysis (if applicable) and before the footer. Each diagram is:
- Centred on the page
- Scaled proportionally to fit the available page width (A4 minus margins)
- Maintains its original canvas aspect ratio so that axis labels, tick numbers, and chart text remain fully readable
- Labelled with a descriptive title

### 4.29.7 Implementation Files

| File | Change |
|---|---|
| `api/static/script.js` | Added canvas capture logic in `downloadResults()` using `toDataURL()` |
| `api/report.py` | Added base64 decoding, `Image` import, and Section 9 diagram rendering |


## 4.30 Beam Diagram Visual Improvements

### 4.30.1 Unified Colour Scheme

All beam type diagrams (simply supported, cantilever, overhang) were updated to use the same colour palette as the continuous beam diagram, replacing the previous white-only rendering.

| Element | Colour | Hex Code |
|---|---|---|
| Beam line | Blue | `#3b82f6` |
| Pinned support | Green | `#10b981` |
| Roller support | Amber | `#f59e0b` |
| Fixed support | Red | `#ef4444` |
| Span labels | Amber (bold) | `#f59e0b` |
| Support labels (A, B, C) | Green (bold) | `#10b981` |
| UDL arrows & labels | Green | `#10b981` |

The `drawSupport()` function now applies per-type colouring, matching the separate `drawPinnedSupport()`, `drawRollerSupport()`, and `drawFixedSupport()` functions used by the continuous beam diagram.

### 4.30.2 Continuous Beam Dimension Tick Marks

The span dimension lines in the continuous beam diagram were enhanced with vertical tick marks at each boundary:

- **Left tick**: Drawn at the start of each span's dashed line
- **Right tick**: Drawn at the end of each span's dashed line
- **Tick height**: 5px above and below the dimension line centre

This makes span boundaries clearly demarcated, especially where adjacent spans share a support point.

### 4.30.3 PDF Chart Diagram Improvements

Two improvements were made to the Chart.js diagrams embedded in the PDF results report:

1. **Dark Background**: Each Chart.js diagram (load, shear, moment) is composited onto a dark background (`#1e293b`) using Pillow before embedding. This ensures the white axis labels, tick numbers, and chart text remain fully visible on the white PDF page.

2. **Spacing**: Diagram spacing was increased to 14pt between charts, providing comfortable visual separation while still fitting all three on a single A4 page.

### 4.30.4 Implementation Files

| File | Change |
|---|---|
| `api/static/script.js` | Updated `drawBeamDiagram()`, `drawSupport()` with coloured elements; added vertical ticks to `drawContinuousBeamDiagram()` |
| `api/report.py` | Added Pillow-based dark background compositing; increased chart spacing to 14pt |


## 4.31 Beam Design Calculation Sheet (Download Calculation Sheet)

### 4.31.1 Overview

A comprehensive **Beam Design Calculation Sheet** PDF was implemented, modelled after professional structural engineering software output (e.g., Orion Building Design System). When the user clicks **"Download Calculation Sheet"** from the download modal, the system generates a detailed, multi-section PDF containing all BS 8110 design calculations, embedded diagrams, and a reinforcement schedule.

This replaces the previous `501 Not Implemented` placeholder on the `/download-calculation-sheet` endpoint.

### 4.31.2 PDF Layout Structure

The calculation sheet contains 8 sections:

| Section | Content |
|---|---|
| 1. Header | System name, beam type, material grades (C_fcu_/Grade fy), load type |
| 2. Beam Geometry | Beam size (b × h), span(s), support types, material properties |
| 3. Load Breakdown | n1 (slab load), n2 (self-weight), n3 (wall load), p1 (point load), w (total UDL) |
| 4. Diagrams | Beam diagram, Load diagram, Shear Force Diagram, Bending Moment Diagram |
| 5. Bending Design | Full BS 8110 bending design — M, Mu, d, K, K', z, As_req, As_prov, bars |
| 6. Shear Design | V, v, v_max, v_c, link type, stirrups description, status |
| 7. Deflection Check | Basic span/d, fs, MF, allowable vs actual span/d, pass/fail |
| 8. Reinforcement Schedule | Per-location bar schedule with As_req vs As_prov and OK/FAIL status |

### 4.31.3 Beam Type Support

| Beam Type | Bending Table | Reinforcement Schedule |
|---|---|---|
| Simply Supported | Single-section table (Parameter → Symbol → Value → Unit) | Main bars (bottom) + nominal top bars |
| Cantilever | Same single-section format | Same |
| Overhang | Same single-section format | Same |
| Continuous | **Per-location tables**: Top Edge (hogging at supports) + Bottom Edge (sagging at spans) + Support Moments & Reactions summary | Per-location schedule with top/bottom bars at each support/span |

### 4.31.4 Data Flow

```
Frontend: Generate Design → lastDesignData stored
    ↓
User clicks "Download Calculation Sheet"
    ↓
downloadCalculationSheet() captures canvas diagrams as base64 PNG
    ↓
POST /download-calculation-sheet (full design data + diagrams_base64)
    ↓
api/calc_sheet.py → generate_calc_sheet(data) → ReportLab PDF
    ↓
FileResponse → browser downloads "ai_beam_calc_sheet.pdf"
```

### 4.31.5 Visual Design

The calculation sheet uses a professional colour palette:
- **Header**: Dark navy background (`#1e3a5f`) with white text
- **Section headers**: Slate grey background (`#cdd5e0`) with bold text
- **Row labels**: Light grey background (`#e8ecf1`) for parameter names
- **Grid**: Subtle grey borders (`#94a3b8`)
- **Pass/Fail**: Green (`#15803d`) for OK, red (`#dc2626`) for FAIL
- **Chart diagrams**: Dark background compositing (`#1e293b`) for readable white chart text

### 4.31.6 Implementation Files

| File | Change |
|---|---|
| `api/calc_sheet.py` | **New file** — Complete calculation sheet PDF generator with 8 sections |
| `api/main.py` | Updated `/download-calculation-sheet` endpoint; added `generate_calc_sheet` import |
| `api/static/script.js` | Updated `downloadCalculationSheet()` to send full data payload with diagram captures and proper DOM-based file download |
| `api/static/index.html` | Cache bust to v17 |


## 4.32 Custom Project Title Integration

A custom project title feature was integrated to allow users to personalize the generated calculation sheets. 
When the user clicks the "Download PDF" button, a modal prompts them for an optional "Project Title". If provided, this title is injected into the PDF generation payload and elegantly embedded at the top of the Calculation Sheet using a distinguished font colour (`#1e3a5f`), providing professional branding for specific engineering projects.


## 4.33 Factored Wall Loading Update (BS 8110)

The wall loading algorithm was corrected to adhere to standard structural engineering practices. Previously, a raw value (e.g. 2.87) was treated as density. Following engineering review, this was revised to calculate the precise **Wall Line Load** in kN/m using the formula:

`Wall Line Load = Unit Weight × Thickness × Height`

The system now enforces a default unit weight of 20.0 kN/m³ (representing conventional hollow block masonry) unless the user specifically overrides it in the prompt. The resulting Wall Line Load is then factored using the BS 8110 permanent load safety factor (1.4):

`n3 = 1.4 × Wall Line Load`

This corrected calculation is now dynamically presented in both the user interface and the exported PDF calculation sheet load breakdown.


## 4.34 Overhang Beam Handling Improvements

Several issues affecting the presentation of Overhang beams were resolved:

1. **Robust Prompt Parsing**: The natural language parser (`nlp/prompt_parser.py`) was enhanced to recognize diverse overhang definitions in prompts (e.g. `overhang 2m`, `overhang of 2.5m`, `overhang: 2m`, `overhang = 2m`).
2. **Distinct Geometry Display**: The user interface (Results panel) and the generated PDF reports were modified. Previously, the "Span" label was used generically. Now, when an overhang beam is detected, the system distinctly breaks down the total length, explicitly displaying both the main **Span** and the **Overhang Length**.
3. **Diagram Integrity**: The Canvas beam diagram was updated to proportionally render the overhang segment when specified, preventing UI bugs where a zero or undetected overhang defaulted to a standard span rendering.


## 4.35 Enhanced System Branding & UI

### 4.35.1 AI-RCBDS Nomenclature
The system's name was officially updated to **AI-RCBDS (AI Reinforced Concrete Beam Design System)**. The PDF report headers, the calculation sheet titles, and the downloaded PDF filenames were all updated to reflect this new identity (e.g., `ai-rcbds_calc_sheet.pdf` and `ai-rcbds_results_report.pdf`).

### 4.35.2 Landing Page Overlay
A highly immersive, premium landing page overlay was designed for the application. It features:
- A glassmorphism background that blurs a structural engineering background image (`landing-page.webp`).
- An animated gradient text accentuating the system title.
- A prominent "Launch Application" button that gracefully fades out the overlay to reveal the main application interface.

### 4.35.3 System Favicon
A custom favicon (`fuoye.webp`) was linked to the application to provide a professional, recognizable browser tab icon.


## 4.36 Advanced Multi-Span Continuous Beam Solver & Three-Moment Integration

### 4.36.1 Statically Indeterminate Multi-Span Analysis
The system was upgraded to support indeterminate continuous beams of $N$-spans ($2 \le N \le 5$) with heterogeneous span lengths and boundary conditions. The calculation engine incorporates Clapeyron's Three-Moment Theorem (`rules/continuous_beam.py`), constructing a matrix linear system $[A]\{M\} = \{b\}$ to solve for exact support bending moments ($M_A, M_B, M_C, M_D$), reaction forces ($R_A, R_B, R_C, R_D$), and maximum sagging moments in each span.

### 4.36.2 Support Boundary Condition Parsing
The prompt parser (`nlp/prompt_parser.py`) was enhanced to recognize node-by-node support declarations, such as:
- `"Support A is fixed, while B and C are roller supports"` $\rightarrow$ `["fixed", "roller", "roller"]`
- `"Support A and D are fixed, while B and C are roller supports"` $\rightarrow$ `["fixed", "roller", "roller", "fixed"]`

### 4.36.3 Midpoint Load Position Resolution
Point loads specified at relative span locations using keywords such as `"midpoint"`, `"midspan"`, `"center"`, or `"middle"` (e.g. `"10 kN point load acts at the midpoint of BC"`) are resolved mathematically to $L/2$ relative to that specific span ($2.0\text{m}$ for span BC of length $4\text{m}$).


## 4.37 Multi-Point Load Handling & Coordinate-Based UDL Mapping

### 4.37.1 Multiple Point Load Parsing & UI Representation
The NLP prompt parser and modal interface were updated to detect multiple point loads (`p1`, `p2`, `p3`...) and map their positions (`a1`, `a2`, `a3`...). The parameter modal dynamically expands to display individual labels (`POINT LOAD (P1)`, `LOAD POSITION (A1)`, `POINT LOAD (P2)`, `LOAD POSITION (A2)`...) alongside cumulative summary tags.

### 4.37.2 Global Coordinate Range UDL Mapping
For continuous beams specified with global coordinate ranges (e.g., `"A UDL 2 kN/m from 0 to 3m"` or `"A UDL 20 kN/m from 12m to 24m"`), the compiler calculates cumulative span boundary thresholds (`cum_spans = [(0, 12), (12, 24), (24, 28)]`) and maps the UDL load strictly to the matching span index before passing the load array to the Three-Moment Theorem solver.

### 4.37.3 Load Diagram Canvas Filtering
To maintain visual clarity, the HTML5 Canvas beam diagram renderer (`drawContinuousBeamDiagram` in `api/static/script.js`) filters out internal self-weight/dead load entries (`is_dead: True`) and renders user-applied UDLs **strictly on the span where they were applied**, preventing empty spans from incorrectly displaying self-weight UDL boxes while preserving full BS 8110 mathematical load factoring in structural analysis.


## 4.38 Comprehensive PowerShell Terminal Testing Protocol

A standardized command-line manual testing protocol was established and documented in `manual_testing_doc.md`. It provides engineers and reviewers with copy-pasteable PowerShell CLI snippets using `Invoke-RestMethod` to validate all 4 supported beam types (**Simply Supported**, **Cantilever**, **Overhang**, and **Continuous**) across `/parse`, `/predict`, and `/download-calculation-sheet` API endpoints.
