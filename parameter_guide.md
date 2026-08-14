# AI-RCBDS Prompting Guidelines & Parameter Guide (`parameter_guide.md`)

Welcome to the **AI Reinforced Concrete Beam Design System (AI-RCBDS)** Prompting Guidelines. This reference guide outlines standard syntax, prefixes, suffixes, and natural language patterns for declaring beam types, span lengths, material grades, support conditions, and single or multi-span load combinations.

---

## 1. Core Prompting Structure

A complete structural prompt generally follows this hierarchy:
`[Beam Type Prefix] + [Span & Support Specifications] + [Load Specifications] + [Material / Wall Suffixes]`

### Quick Example:
> **"Design a simply supported beam with span 6m, UDL 20kN/m, point load 30kN at 2m, fcu 30, fy 500"**

---

## 2. Beam Type Keywords & Prefixes

The parser identifies the beam configuration based on explicit prefixes or key phrases in your prompt:

| Beam Type | Recognized Keywords / Prefixes | Default Supports |
| :--- | :--- | :--- |
| **Simply Supported** | `simply supported`, `simply supported beam`, `simple beam` | Left: Pinned, Right: Roller |
| **Cantilever** | `cantilever`, `cantilever beam`, `fixed beam` | Left: Fixed, Right: Free |
| **Overhang** | `overhang`, `overhanging beam`, `overhang of Xm`, `Xm overhang` | Left: Pinned, Right: Roller |
| **Continuous** | `continuous`, `continuous beam`, `X-span continuous beam`, `spans Xm Ym`, `beam ABC`, `beam ABCD` | Pinned/Roller interior nodes (Fixed optional) |

---

## 3. Span Specifications & Multi-Span Patterns

### Single Span & Overhang Length
- **Single Span**: `span 6m`, `span of 6m`, `6m span`
- **Overhang Length**: `overhang 2m`, `1.5m overhang`, `overhang of 2m`, `overhang BC of 2m`

### Multi-Span Continuous Beams
- **Explicit List**: `spans 5m, 6m, 5m` or `spans 4m and 5m`
- **Named Spans**: `Span AB is 3 m and span BC is 4 m` $\rightarrow$ `spans: [3.0, 4.0]`
- **Named Multi-Spans**: `Span AB = 12 m, BC = 12 m, and CD = 4 m` $\rightarrow$ `spans: [12.0, 12.0, 4.0]`
- **Uniform Spans**: `3-span continuous beam 6m` (creates 3 spans of 6.0m each: `[6.0, 6.0, 6.0]`)

---

## 4. Loading Parameters & Combination Syntax

AI-RCBDS supports **Uniformly Distributed Loads (UDL)**, **Partial UDLs**, **Global Coordinate Range UDLs**, and **Multiple Discrete Point Loads** (`p1`, `p2`, `p3`...).

### A. Uniformly Distributed Loads (UDL)
- **Full Span UDL**: `UDL 20kN/m`, `UDL of 25 kN/m`, `load 20kN/m`
- **Partial UDL (Relative)**: `UDL 15kN/m from 0 to 3m`, `UDL 20kN/m from 2m to 5m`
- **Global Coordinate Range UDL (Continuous Beams)**: `A UDL 2 kN/m from 0 to 3m` or `A UDL 20 kN/m from 12m to 24m` (maps global bounds to continuous span indices)

### B. Point Loads (`p1`, `p2`, `p3`...)
You can specify multiple point loads in a single beam using natural wording, indexed notation, or midpoint keywords:
- **Single Point Load**: `point load 30kN at 2m`, `30kN point load at 2m`
- **Midpoint Keyword Resolution**: `10 kN point load acts at the midpoint of BC` $\rightarrow$ places point load at $L/2$ ($2.0\text{m}$) of span BC.
- **Indexed Point Loads**: `p1 = 25kN at 2m, p2 = 40kN at 6m`
- **Natural Multiple Point Loads**: `point loads 25kN at 2m and 40kN at 6m`
- **Free End Load (Overhang / Cantilever)**: `point load 10kN at free end`

### C. Combined Loads (UDL + Point Loads)
- `UDL 20kN/m and point load 30kN at 2m`
- `UDL 15kN/m from 0 to 3m and point load 20kN at 4m`

### D. Per-Span Continuous Beam Loads
Specify individual span loading using span identifiers (`span AB`, `span BC`, `first span`, `second span`):
> `3-span continuous beam spans 5m 6m 5m, span AB UDL 20kN/m, span BC UDL 15kN/m and point load 30kN at 2m, span CD point load 25kN at 3m`

---

## 5. Support Conditions & Boundary Constraints

The system parses both explicit support lists and node-by-node support declarations:

- **Single Span**: `left support is pinned, right support is roller`
- **Fixed End Override**: `fixed at A`, `fixed at start`, `fixed at end`
- **Named Node Declarations**:
  - `Support A is fixed, while B and C are roller supports` $\rightarrow$ `supports: ["fixed", "roller", "roller"]`
  - `Support A and D are fixed, while B and C are roller supports` $\rightarrow$ `supports: ["fixed", "roller", "roller", "fixed"]`
- **Multiple Supports List**: `supports: fixed, pinned, roller, pinned`

---

## 6. Material & Secondary Load Suffixes

Append material grades or wall/slab dimensions anywhere in the prompt (usually as suffixes):

| Parameter | Prefix / Suffix Keywords | Example | Default Value |
| :--- | :--- | :--- | :--- |
| **Concrete Grade ($f_{cu}$)** | `fcu X`, `fck X`, `grade X`, `concrete grade X` | `fcu 30` | 25.0 N/mm² |
| **Steel Grade ($f_y$)** | `fy X`, `steel grade X`, `X MPa` | `fy 500` | 460.0 N/mm² |
| **Wall Height** | `wall height X`, `height X` | `wall height 3m` | 0.0 m |
| **Wall Thickness** | `wall thickness X`, `thickness X` | `thickness 0.23m` | 0.0 m |
| **Masonry Density** | `density X`, `unit weight X` | `density 20` | 20.0 kN/m³ |
| **Slab Loading** | `slab load X` | `slab load 15kN/m` | 0.0 kN/m |

---

## 7. Standardized Prompt Examples

Below are standard prompts designed to test every loading style in the system:

```text
1. Simply Supported (Combined Load):
   "Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m, fcu 30, fy 500"

2. Simply Supported (Multiple Point Loads):
   "Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m"

3. Partial UDL + Point Load:
   "Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m"

4. Overhang Beam (UDL + Free End Load):
   "Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end"

5. Continuous Beam - Prompt 1 (Fixed-Roller-Roller, Midpoint Load, Partial Range UDL):
   "Analyze the continuous beam ABC. Support A is fixed, while B and C are roller supports. Span AB is 3 m and span BC is 4 m. A UDL 2 kN/m from 0 to 3m, while a 10 kN point load acts at the midpoint of BC."

6. Continuous Beam - Prompt 2 (Fixed-Roller-Roller-Fixed, Middle Span Coordinate UDL):
   "Analyze the continuous beam ABCD. Support A and D are fixed, while B and C are roller supports. Span AB = 12 m, BC = 12 m, and CD = 4 m. A UDL 20 kN/m from 12m to 24m, while a 250 kN point load acts at the midpoint of span CD."
```
