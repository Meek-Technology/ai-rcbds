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