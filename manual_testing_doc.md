# AI-RCBDS Manual PowerShell Terminal Testing Protocol (`manual_testing_doc.md`)

This document provides step-by-step instructions for manually testing all structural beam types (**Simply Supported**, **Cantilever**, **Overhang**, and **Multi-Span Continuous**) using PowerShell REST requests (`Invoke-RestMethod` and `curl.exe`).

---

## 1. Environment Setup & Server Health Check

Ensure the FastAPI server is running locally:
```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Health Check Request:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method Get
```
**Expected Response:**
```json
{
  "message": "AI Structural Design API is running."
}
```

---

## 2. API Flow Overview

The system uses a 2-step API execution workflow:
1. **`/parse` (POST)**: Converts free-text natural language prompts into parsed JSON parameters.
2. **`/predict` (POST)**: Executes BS 8110 engineering calculations, Three-Moment matrix solving, ML reinforcement prediction, and returns graph curves.

---

## 3. Testing Beam Type 1: Simply Supported Beam

### Test 1.1: Combined UDL + Single Point Load
**Prompt:** `"Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m, fcu 30, fy 500"`

#### Step 1: Parse Prompt
```powershell
$body = @{ prompt = "Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m, fcu 30, fy 500" } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$parsed.parsed | ConvertTo-Json -Depth 5
```

#### Step 2: Run Full Design & Prediction
```powershell
$predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body $predictBody
$result.results | ConvertTo-Json
```

### Test 1.2: Multiple Point Loads (`p1`, `p2`)
**Prompt:** `"Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m"`
```powershell
$body = @{ prompt = "Design a simply supported beam span 8m with point loads 25kN at 2m and 40kN at 6m" } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$parsed.parsed.loads | ConvertTo-Json
```

### Test 1.3: Partial UDL + Point Load
**Prompt:** `"Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m"`
```powershell
$body = @{ prompt = "Simply supported beam 5m span, UDL 15kN/m from 0 to 3m and point load 20kN at 4m" } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$parsed.parsed.loads | ConvertTo-Json
```

---

## 4. Testing Beam Type 2: Cantilever Beam

### Test 2.1: UDL + End Point Load
**Prompt:** `"Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m"`

```powershell
$body = @{ prompt = "Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m" } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body $predictBody

Write-Host "Cantilever Bending Moment:" $result.results.bending_moment "kNm"
Write-Host "Reinf Recommended:" $result.reinforcement.recommended
```

---

## 5. Testing Beam Type 3: Overhang Beam

### Test 3.1: Span UDL + Free End Load
**Prompt:** `"Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end"`

```powershell
$body = @{ prompt = "Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end" } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body $predictBody

Write-Host "Overhang Main Span:" $result.input.span "m | Overhang:" $result.input.overhang_length "m"
Write-Host "Governing Moment:" $result.design.M "kNm"
```

---

## 6. Testing Beam Type 4: Multi-Span Continuous Beams

### Test 4.1: 2-Span Continuous Beam with Midpoint Point Load (Prompt 1)
**Prompt:** `"Analyze the continuous beam ABC. Support A is fixed, while B and C are roller supports. Span AB is 3 m and span BC is 4 m. A UDL 2 kN/m from 0 to 3m, while a 10 kN point load acts at the midpoint of BC."`

```powershell
$body = @{ prompt = "Analyze the continuous beam ABC. Support A is fixed, while B and C are roller supports. Span AB is 3 m and span BC is 4 m. A UDL 2 kN/m from 0 to 3m, while a 10 kN point load acts at the midpoint of BC." } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body $predictBody

Write-Host "Spans:" ($result.continuous.spans -join ", ") "m"
Write-Host "Supports:" ($result.continuous.supports -join " -> ")
Write-Host "Support Moments (kNm):" ($result.continuous.support_moments -join ", ")
Write-Host "Reactions (kN):" ($result.continuous.reactions -join ", ")
```

### Test 4.2: 3-Span Continuous Beam with Global Coordinate UDL (Prompt 2)
**Prompt:** `"Analyze the continuous beam ABCD. Support A and D are fixed, while B and C are roller supports. Span AB = 12 m, BC = 12 m, and CD = 4 m. A UDL 20 kN/m from 12m to 24m, while a 250 kN point load acts at the midpoint of span CD."`

```powershell
$body = @{ prompt = "Analyze the continuous beam ABCD. Support A and D are fixed, while B and C are roller supports. Span AB = 12 m, BC = 12 m, and CD = 4 m. A UDL 20 kN/m from 12m to 24m, while a 250 kN point load acts at the midpoint of span CD." } | ConvertTo-Json
$parsed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/parse" -Method Post -ContentType "application/json" -Body $body
$predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body $predictBody

Write-Host "Spans:" ($result.continuous.spans -join ", ") "m"
Write-Host "Supports:" ($result.continuous.supports -join " -> ")
Write-Host "Support Moments (kNm):" ($result.continuous.support_moments -join ", ")
Write-Host "Reactions (kN):" ($result.continuous.reactions -join ", ")
```

---

## 7. PDF Report Download Testing

### Test 7.1: Download BS 8110 Calculation Sheet PDF
```powershell
$payload = @{
    data = $result
    diagrams_base64 = @{}
    project_title = "PowerShell Test Project"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/download-calculation-sheet" -Method Post -ContentType "application/json" -Body $payload -OutFile "test_powershell_calc_sheet.pdf"
Write-Host "Calculation sheet saved to test_powershell_calc_sheet.pdf"
```

---

## 8. Automated PowerShell Test Runner Script

Copy and execute this script block in PowerShell to test all 4 beam types automatically:

```powershell
$baseUrl = "http://127.0.0.1:8000"
$prompts = @(
    @{ Type = "Simply Supported"; Prompt = "Design a simply supported beam with span 6m, UDL 20kN/m and point load 30kN at 2m, fcu 30, fy 500" },
    @{ Type = "Cantilever"; Prompt = "Cantilever beam 3m, UDL 10kN/m and point load 15kN at 3m" },
    @{ Type = "Overhang"; Prompt = "Overhang beam span 6m overhang 2m, UDL 15kN/m on span and point load 10kN at free end" },
    @{ Type = "Continuous 2-Span"; Prompt = "Analyze the continuous beam ABC. Support A is fixed, while B and C are roller supports. Span AB is 3 m and span BC is 4 m. A UDL 2 kN/m from 0 to 3m, while a 10 kN point load acts at the midpoint of BC." },
    @{ Type = "Continuous 3-Span"; Prompt = "Analyze the continuous beam ABCD. Support A and D are fixed, while B and C are roller supports. Span AB = 12 m, BC = 12 m, and CD = 4 m. A UDL 20 kN/m from 12m to 24m, while a 250 kN point load acts at the midpoint of span CD." }
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI-RCBDS POWERSHELL REST API COMPREHENSIVE TEST SUITE  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

foreach ($item in $prompts) {
    Write-Host "`nTesting $($item.Type)..." -ForegroundColor Yellow
    try {
        $body = @{ prompt = $item.Prompt } | ConvertTo-Json
        $parsed = Invoke-RestMethod -Uri "$baseUrl/parse" -Method Post -ContentType "application/json" -Body $body
        $predictBody = $parsed.parsed | ConvertTo-Json -Depth 5
        $res = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType "application/json" -Body $predictBody

        Write-Host " [PASS] Parsed Beam Type: $($res.input.beam_type)" -ForegroundColor Green
        Write-Host " [PASS] Max Moment: $($res.results.bending_moment) kNm" -ForegroundColor Green
        Write-Host " [PASS] Recommended Reinf: $($res.reinforcement.recommended)" -ForegroundColor Green
    } catch {
        Write-Host " [FAIL] Exception: $_" -ForegroundColor Red
    }
}
Write-Host "`n==========================================================" -ForegroundColor Cyan
```
