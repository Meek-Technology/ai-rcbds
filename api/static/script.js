let shearChart, momentChart, loadChart;

// Store parsed params between modal steps
let pendingParams = null;

// ═══════════════════════════════════════════════
//  LANDING PAGE
// ═══════════════════════════════════════════════

function closeLandingPage() {
    const overlay = document.getElementById("landingOverlay");
    if (overlay) {
        overlay.classList.add("hidden");
        // Remove from DOM after transition completes
        setTimeout(() => overlay.remove(), 700);
    }
    // Scroll main page to top
    window.scrollTo({ top: 0, behavior: 'instant' });
}

// ═══════════════════════════════════════════════
//  STEP 1: Parse prompt → Show modal
// ═══════════════════════════════════════════════

async function handleGenerate() {
    const prompt = document.getElementById("prompt").value.trim();
    if (!prompt) {
        alert("Please enter a beam design prompt first.");
        return;
    }

    const loader = document.getElementById("loader");
    loader.style.display = "block";

    try {
        const response = await fetch("/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();
        loader.style.display = "none";

        if (data.error) {
            alert("Parsing Error: " + data.error);
            return;
        }

        pendingParams = data.parsed;
        showModal(data.parsed);

    } catch (error) {
        console.error("Parse error:", error);
        loader.style.display = "none";
        alert("Failed to parse prompt. Check console for details.");
    }
}


// ═══════════════════════════════════════════════
//  MODAL FUNCTIONS
// ═══════════════════════════════════════════════

function showModal(params) {
    const grid = document.getElementById("parsedParams");

    // Parameter definitions: [key, label, unit, highlight?, explicitValue?]
    const fields = [
        ["beam_type", "Beam Type", "", true],
        ["load_type", "Load Type", "", true],
        ["span", "Span", "m", false],
        ["load", "Load", "kN/m", false],
        ["slab_load", "Slab Load (n1)", "kN/m", false],
    ];

    // Dynamic point load fields (p1, a1, p2, a2, p3, a3...)
    const pointLoadList = params.point_loads || (params.loads ? params.loads.filter(ld => ld.type === "point_load") : []);
    if (pointLoadList.length > 0) {
        pointLoadList.forEach((pl, idx) => {
            const num = idx + 1;
            const posLabel = pointLoadList.length > 1 ? `Load Position (a${num})` : "Load Position (a1)";
            fields.push([`p${num}`, `Point Load (p${num})`, "kN", false, pl.P]);
            if (pl.a !== undefined && pl.a !== null) {
                fields.push([`a${num}`, posLabel, "m", false, pl.a]);
            }
        });
    } else {
        if (params.point_load) {
            fields.push(["point_load", "Point Load (p1)", "kN", false, params.point_load]);
        }
        if (params.load_position) {
            fields.push(["load_position", "Load Position (a1)", "m", false, params.load_position]);
        }
    }

    fields.push(
        ["overhang_length", "Overhang Length", "m", false],
        ["fcu", "Concrete (fcu)", "N/mm²", false],
        ["fy", "Steel (fy)", "N/mm²", false],
        ["support_left", "Left Support", "", false],
        ["support_right", "Right Support", "", false],
        ["wall_height", "Wall Height", "m", false],
        ["wall_thickness", "Wall Thickness", "m", false],
        ["density", "Wall Unit Weight", "kN/m³", false]
    );

    const typeLabels = {
        "simply_supported": "Simply Supported",
        "cantilever": "Cantilever",
        "continuous": "Continuous",
        "overhang": "Overhang"
    };
    const loadLabels = {
        "udl": "UDL (Uniformly Distributed)",
        "point_load": "Point Load",
        "combined": "Combined (UDL + Point Loads)",
        "triangular": "Triangular"
    };

    let html = "";

    for (const item of fields) {
        const [key, label, unit, highlight, explicitVal] = item;
        let val = explicitVal !== undefined ? explicitVal : params[key];

        // Skip null/zero optional fields
        if (val === null || val === undefined) continue;
        if (val === 0 && ["load", "slab_load", "point_load", "wall_height", "wall_thickness", "overhang_length", "load_position"].includes(key)) continue;

        // For continuous beams, skip single span/support (we show multi-span instead)
        if (params.spans && ["span", "support_left", "support_right"].includes(key)) continue;

        // Format display value
        if (key === "beam_type") val = typeLabels[val] || val;
        if (key === "load_type") val = loadLabels[val] || val;
        if (key === "support_left" || key === "support_right") val = capitalize(val);

        const displayVal = unit ? `${val} ${unit}` : val;
        const hlClass = highlight ? " highlight" : "";
        const fullClass = (key === "beam_type" || key === "load_type") ? " full-width" : "";

        html += `
            <div class="param-item${fullClass}">
                <span class="param-label">${label}</span>
                <span class="param-value${hlClass}">${displayVal}</span>
            </div>
        `;
    }

    // ── Multi-span display for continuous beams ──
    if (params.spans && params.spans.length > 0) {
        const spansStr = params.spans.map(s => s + "m").join(" → ");
        html += `
            <div class="param-item full-width">
                <span class="param-label">Spans (${params.spans.length})</span>
                <span class="param-value highlight">${spansStr}</span>
            </div>
        `;
    }

    if (params.supports && params.supports.length > 0) {
        const supStr = params.supports.map(s => capitalize(s)).join(" → ");
        html += `
            <div class="param-item full-width">
                <span class="param-label">Supports (${params.supports.length})</span>
                <span class="param-value">${supStr}</span>
            </div>
        `;
    }

    // ── Multi-load display ──
    if (params.per_span_loads && params.per_span_loads.length > 0) {
        html += `<div class="param-item full-width"><span class="param-label">Per-Span Loads</span><div style="font-size: 0.9em;">`;
        params.per_span_loads.forEach((spanLoads, idx) => {
            const letterLeft = String.fromCharCode(65 + idx);
            const letterRight = String.fromCharCode(66 + idx);
            html += `<strong>Span ${letterLeft}${letterRight}:</strong><ul>`;
            spanLoads.forEach(ld => {
                if (ld.type === "udl") html += `<li>UDL: ${ld.w} kN/m</li>`;
                if (ld.type === "point_load") html += `<li>Point Load: ${ld.P} kN at ${ld.a}m</li>`;
            });
            html += `</ul>`;
        });
        html += `</div></div>`;
    } else if (params.loads && params.loads.length > 0) {
        html += `<div class="param-item full-width"><span class="param-label">Combined / Multiple Loads</span><ul>`;
        let pCount = 0;
        params.loads.forEach(ld => {
            if (ld.type === "udl") {
                let text = `UDL: ${ld.w} kN/m`;
                if (ld.start !== undefined && ld.end !== undefined) {
                    text += ` (from ${ld.start}m to ${ld.end}m)`;
                }
                html += `<li>${text}</li>`;
            }
            if (ld.type === "point_load") {
                pCount++;
                let text = `Point Load (p${pCount}): ${ld.P} kN`;
                if (ld.a !== undefined && ld.a !== null) text += ` at ${ld.a}m`;
                html += `<li>${text}</li>`;
            }
        });
        html += `</ul></div>`;
    }

    grid.innerHTML = html;

    // Show modal
    document.getElementById("parseModal").classList.add("active");
}

function closeModal() {
    document.getElementById("parseModal").classList.remove("active");
    pendingParams = null;
}

// ═══════════════════════════════════════════════
//  STEP 2: Confirm → Run full design
// ═══════════════════════════════════════════════

async function confirmGenerate() {
    closeModal();
    const prompt = document.getElementById("prompt").value;
    await generate(prompt);
}


// ═══════════════════════════════════════════════
//  RESET UI — clear all previous results & charts
// ═══════════════════════════════════════════════

function resetUI() {
    // Clear text result fields
    const textIds = [
        "beamType", "loadType", "support", "beamSpan", "overhangLength",
        "n1", "n2", "n3", "wTotal", "p1",
        "mUdl", "mPoint", "moment", "shear", "steel",
        "reinf", "beam", "deflection"
    ];
    textIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = "";
    });

    // Hide overhang row
    const ohRow = document.getElementById("overhangRow");
    if (ohRow) ohRow.style.display = "none";

    // Hide & clear dynamic sections
    const dynamicIds = ["designData", "continuousData"];
    dynamicIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = "";
            el.style.display = "none";
        }
    });

    // Destroy existing Chart.js instances
    if (shearChart) { shearChart.destroy(); shearChart = null; }
    if (momentChart) { momentChart.destroy(); momentChart = null; }
    if (loadChart) { loadChart.destroy(); loadChart = null; }

    // Reset beam diagram canvas (dimensions + content)
    const canvas = document.getElementById("beamCanvas");
    if (canvas) {
        canvas.width = 600;
        canvas.height = 200;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}


async function generate(prompt) {
    try {
        // Reset all previous results before generating new ones
        resetUI();

        const loader = document.getElementById("loader");
        loader.style.display = "block";

        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        loader.style.display = "none";

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // Store full response for PDF downloads
        lastDesignData = data;

        // ── Beam type & load type labels ──
        const typeLabels = {
            "simply_supported": "Simply Supported",
            "cantilever": "Cantilever",
            "continuous": "Continuous",
            "overhang": "Overhang"
        };
        const loadLabels = {
            "udl": "UDL (Uniformly Distributed)",
            "point_load": "Point Load",
            "combined": "Combined (UDL + Point Loads)",
            "triangular": "Triangular"
        };

        document.getElementById("beamType").innerText =
            typeLabels[data.input.beam_type] || data.input.beam_type;
        document.getElementById("loadType").innerText =
            loadLabels[data.input.load_type] || data.input.load_type;

        // Support display — continuous vs single-span
        if (data.continuous) {
            const supStr = data.continuous.supports.map(s => capitalize(s)).join(" → ");
            document.getElementById("support").innerText = supStr;
        } else {
            document.getElementById("support").innerText =
                capitalize(data.input.support_left) + " — " + capitalize(data.input.support_right);
        }

        // ── Span & Overhang display ──
        if (data.continuous) {
            document.getElementById("beamSpan").innerText =
                data.continuous.spans.map(s => s + "m").join(" + ");
            document.getElementById("overhangRow").style.display = "none";
        } else {
            document.getElementById("beamSpan").innerText = data.input.span + " m";
            const ohLen = data.input.overhang_length || 0;
            if (data.input.beam_type === "overhang" && ohLen > 0) {
                document.getElementById("overhangRow").style.display = "block";
                document.getElementById("overhangLength").innerText = ohLen + " m";
            } else {
                document.getElementById("overhangRow").style.display = "none";
            }
        }

        // ── Load Breakdown ──
        document.getElementById("n1").innerText = data.results.n1_slab_load + " kN/m";
        document.getElementById("n2").innerText = data.results.n2_beam_self_weight + " kN/m";
        document.getElementById("n3").innerText = data.results.n3_wall_load + " kN/m";
        document.getElementById("wTotal").innerText = data.results.w_total_udl + " kN/m";

        if (data.results.all_point_loads && data.results.all_point_loads.length > 1) {
            const plStr = data.results.all_point_loads.map((pl, idx) => `p${idx + 1} = ${pl.P} kN${pl.a !== undefined && pl.a !== null ? ' at ' + pl.a + 'm' : ''}`).join(", ");
            document.getElementById("p1").innerText = plStr;
        } else {
            document.getElementById("p1").innerText = (data.results.p1_point_load || 0) + " kN";
        }

        // ── Design Results ──
        document.getElementById("mUdl").innerText = data.results.M_udl + " kNm";
        document.getElementById("mPoint").innerText = data.results.M_point + " kNm";
        document.getElementById("moment").innerText = data.results.bending_moment + " kNm";
        document.getElementById("shear").innerText = data.results.max_shear_force + " kN";
        document.getElementById("steel").innerText = data.results.steel_area + " mm\u00B2";

        document.getElementById("reinf").innerText =
            data.reinforcement.recommended +
            " (As_prov: " + data.reinforcement.provided_area + " mm\u00B2)";

        // Beam size (with resize indicator)
        let beamText = data.beam.width + "mm x " + data.beam.depth + "mm";
        if (data.beam.resized) beamText += " (RESIZED)";
        document.getElementById("beam").innerText = beamText;

        // Deflection — now an object with full BS 8110 data
        const defl = data.deflection;
        if (typeof defl === "object") {
            const deflColor = defl.status === "SAFE" ? "#10b981" : "#ef4444";
            document.getElementById("deflection").innerHTML =
                `<span style="color:${deflColor}; font-weight:bold;">${defl.status}</span>` +
                ` (span/d = ${defl.actual_ratio} ≤ ${defl.allowable_ratio})`;
        } else {
            document.getElementById("deflection").innerText = defl;
        }

        // ── BS 8110 Design Breakdown ──
        const designDiv = document.getElementById("designData");
        if (data.design && designDiv) {
            let html = `<h4 style="margin-top:12px; opacity:0.8;">BS 8110 Bending Design</h4>`;
            html += `<div class="result-item">M<sub>u</sub> (Moment of Resistance): <strong>${data.design.Mu} kNm</strong></div>`;
            html += `<div class="result-item">d (Effective Depth): <strong>${data.design.d} mm</strong></div>`;
            html += `<div class="result-item">K = M/(f<sub>cu</sub>bd\u00B2): <strong>${data.design.K}</strong>`;
            if (data.design.K !== data.design.K_used) {
                html += ` (capped at ${data.design.K_used})`;
            }
            html += `</div>`;
            html += `<div class="result-item">z (Lever Arm): <strong>${data.design.z} mm</strong></div>`;
            html += `<div class="result-item">A<sub>s</sub> required: <strong>${data.results.steel_area} mm\u00B2</strong></div>`;
            html += `<div class="result-item">A<sub>s</sub> provided: <strong>${data.reinforcement.provided_area} mm\u00B2</strong></div>`;

            const statusColor = data.design.adequate ? "#10b981" : "#ef4444";
            html += `<div class="result-item" style="color:${statusColor};"><strong>${data.design.message}</strong></div>`;

            // ── BS 8110 Deflection Check ──
            if (typeof defl === "object") {
                html += `<h4 style="margin-top:16px; opacity:0.8;">BS 8110 Deflection Check</h4>`;
                html += `<div class="result-item">Basic span/d ratio: <strong>${defl.basic_ratio}</strong></div>`;
                html += `<div class="result-item">Service Stress f<sub>s</sub>: <strong>${defl.fs} N/mm\u00B2</strong></div>`;
                html += `<div class="result-item">Modification Factor (MF): <strong>${defl.MF}</strong>`;
                if (defl.MF_uncapped > 2.0) {
                    html += ` <span style="color:#f59e0b;">(capped from ${defl.MF_uncapped})</span>`;
                }
                html += `</div>`;
                html += `<div class="result-item">Allowable span/d: <strong>${defl.allowable_ratio}</strong> (${defl.basic_ratio} × ${defl.MF})</div>`;
                html += `<div class="result-item">Actual span/d: <strong>${defl.actual_ratio}</strong></div>`;
                const deflColor = defl.status === "SAFE" ? "#10b981" : "#ef4444";
                html += `<div class="result-item" style="color:${deflColor};"><strong>${defl.message}</strong></div>`;
                if (defl.fixed) {
                    html += `<div class="result-item" style="color:#f59e0b;"><strong>⚠ Reinforcement/depth adjusted to satisfy deflection</strong></div>`;
                }
            }

            // ── BS 8110 Shear Reinforcement Design ──
            if (data.shear_design) {
                const sd = data.shear_design;
                html += `<h4 style="margin-top:16px; opacity:0.8;">BS 8110 Shear Reinforcement Design</h4>`;
                html += `<div class="result-item">Ultimate Shear Force (V): <strong>${sd.V_kN} kN</strong></div>`;
                html += `<div class="result-item">Shear Stress (v = V/bd): <strong>${sd.v} N/mm\u00B2</strong></div>`;
                html += `<div class="result-item">Ultimate Shear Limit (v<sub>max</sub>): <strong>${sd.v_max} N/mm\u00B2</strong></div>`;
                html += `<div class="result-item">Concrete Shear Capacity (v<sub>c</sub>): <strong>${sd.vc} N/mm\u00B2</strong></div>`;
                if (sd.link_type) {
                    const typeLabel = sd.link_type === "design" ? "Design links" :
                        sd.link_type === "minimum" ? "Minimum links" : "Nominal links";
                    html += `<div class="result-item">Link Type: <strong>${typeLabel}</strong></div>`;
                }
                html += `<div class="result-item">Stirrups Provided: <strong>${sd.link_description}</strong></div>`;
                const shearColor = sd.status === "SAFE" ? "#10b981" : "#ef4444";
                html += `<div class="result-item" style="color:${shearColor};"><strong>${sd.message}</strong></div>`;
            }

            designDiv.innerHTML = html;
            designDiv.style.display = "block";
        } else if (designDiv) {
            designDiv.innerHTML = "";
            designDiv.style.display = "none";
        }

        // ── Continuous Beam Extra Data ──
        const contDiv = document.getElementById("continuousData");
        if (data.continuous && contDiv) {
            let html = `<h4 style="margin-top:12px; opacity:0.8;">Continuous Beam Analysis (Three-Moment Theorem)</h4>`;
            html += `<div class="result-item"><strong>Spans:</strong> ${data.continuous.spans.map(s => s + "m").join(" + ")} (${data.continuous.n_spans}-span)</div>`;

            // Support moments table
            html += `<div class="result-item"><strong>Support Moments:</strong></div>`;
            for (let i = 0; i < data.continuous.support_moments.length; i++) {
                const label = String.fromCharCode(65 + i);
                const m = data.continuous.support_moments[i];
                html += `<div class="result-item">&nbsp;&nbsp;M<sub>${label}</sub> = ${m.toFixed(2)} kNm</div>`;
            }

            // Reactions table
            html += `<div class="result-item"><strong>Support Reactions:</strong></div>`;
            for (let i = 0; i < data.continuous.reactions.length; i++) {
                const label = String.fromCharCode(65 + i);
                const r = data.continuous.reactions[i];
                html += `<div class="result-item">&nbsp;&nbsp;R<sub>${label}</sub> = ${r.toFixed(2)} kN</div>`;
            }

            // ── Per-Location Reinforcement Design Table ──
            if (data.continuous.support_designs || data.continuous.span_designs) {
                html += `<h4 style="margin-top:12px; opacity:0.8;">Reinforcement Design (Per Location)</h4>`;
                html += `<table style="width:100%; border-collapse:collapse; margin:8px 0; font-size:13px;">`;
                html += `<thead><tr style="border-bottom:1px solid rgba(255,255,255,0.2);">
                    <th style="text-align:left; padding:4px;">Location</th>
                    <th style="text-align:left; padding:4px;">Type</th>
                    <th style="text-align:right; padding:4px;">M (kNm)</th>
                    <th style="text-align:right; padding:4px;">K</th>
                    <th style="text-align:right; padding:4px;">z (mm)</th>
                    <th style="text-align:right; padding:4px;">As_req</th>
                    <th style="text-align:left; padding:4px;">Reinf.</th>
                </tr></thead><tbody>`;

                // Support designs (hogging)
                if (data.continuous.support_designs) {
                    for (const sd of data.continuous.support_designs) {
                        if (sd.As_req > 0) {
                            html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.1); color:#ef4444;">
                                <td style="padding:3px 4px;">${sd.location}</td>
                                <td style="padding:3px 4px;">${sd.type}</td>
                                <td style="text-align:right; padding:3px 4px;">${sd.M.toFixed(2)}</td>
                                <td style="text-align:right; padding:3px 4px;">${sd.K.toFixed(5)}</td>
                                <td style="text-align:right; padding:3px 4px;">${sd.z.toFixed(1)}</td>
                                <td style="text-align:right; padding:3px 4px;">${sd.As_req.toFixed(1)}</td>
                                <td style="padding:3px 4px;">${sd.reinforcement}</td>
                            </tr>`;
                        }
                    }
                }

                // Span designs (sagging)
                if (data.continuous.span_designs) {
                    for (const sd of data.continuous.span_designs) {
                        html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.1); color:#10b981;">
                            <td style="padding:3px 4px;">${sd.location}</td>
                            <td style="padding:3px 4px;">${sd.type}</td>
                            <td style="text-align:right; padding:3px 4px;">${sd.M.toFixed(2)}</td>
                            <td style="text-align:right; padding:3px 4px;">${sd.K.toFixed(5)}</td>
                            <td style="text-align:right; padding:3px 4px;">${sd.z.toFixed(1)}</td>
                            <td style="text-align:right; padding:3px 4px;">${sd.As_req.toFixed(1)}</td>
                            <td style="padding:3px 4px;">${sd.reinforcement}</td>
                        </tr>`;
                    }
                }

                html += `</tbody></table>`;
            }

            contDiv.innerHTML = html;
            contDiv.style.display = "block";
        } else if (contDiv) {
            contDiv.innerHTML = "";
            contDiv.style.display = "none";
        }

        drawCharts(data.graphs);

        // Draw beam diagram — multi-span or single-span
        if (data.continuous) {
            drawContinuousBeamDiagram(data.continuous, data.results.n1_slab_load);
        } else {
            drawBeamDiagram(data.input);
        }

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("loader").style.display = "none";
        alert("Something went wrong. Check your console and try again!\nMake sure you're connected to the internet to load graphs.");
    }
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function drawCharts(graphs) {

    const peak = getMaxPoint(graphs.moment);

    const ctx1 = document.getElementById("shearChart").getContext("2d");
    const ctx2 = document.getElementById("momentChart").getContext("2d");
    const ctx3 = document.getElementById("loadChart").getContext("2d");

    if (shearChart) shearChart.destroy();
    if (momentChart) momentChart.destroy();
    if (loadChart) loadChart.destroy();

    const options = (titleText) => ({
        responsive: true,
        animation: {
            duration: 1500,
            easing: "easeOutQuart"
        },

        plugins: {
            legend: {
                labels: { color: "#ffffff" }
            },
            title: {
                display: true,
                text: titleText,
                color: "#ffffff"
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return context.dataset.label + ": " + context.raw.toFixed(2);
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: { color: "#ffffff" },
                grid: { color: "rgba(255,255,255,0.1)" }
            },
            y: {
                ticks: { color: "#ffffff" },
                grid: { color: "rgba(255,255,255,0.1)" }
            }
        }
    });

    shearChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Shear Force (kN)",
                data: graphs.shear,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59,130,246,0.2)",
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: options("Shear Force Diagram")
    });

    momentChart = new Chart(ctx2, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Bending Moment (kNm)",
                data: graphs.moment,
                borderColor: "#f59e0b",
                backgroundColor: "rgba(245,158,11,0.2)",
                fill: true,
                tension: 0.4,
                pointRadius: function (ctx) {
                    return ctx.dataIndex === peak.index ? 6 : 0;
                },
                pointBackgroundColor: "#ff0000"
            }]
        },
        options: options("Bending Moment Diagram")
    });

    loadChart = new Chart(ctx3, {
        type: "line",
        data: {
            labels: graphs.x,
            datasets: [{
                label: "Load (kN/m)",
                data: graphs.load,
                borderColor: "#10b981",
                backgroundColor: "rgba(16,185,129,0.2)",
                fill: true,
                tension: 0,
                pointRadius: 0
            }]
        },
        options: options("Load Diagram")
    });
}

function getMaxPoint(data) {
    let max = Math.max(...data);
    let index = data.indexOf(max);
    return { max, index };
}


// ═══════════════════════════════════════════════
//  BEAM DIAGRAM — Draws beam, supports & loads
// ═══════════════════════════════════════════════

function drawBeamDiagram(input) {
    const canvas = document.getElementById("beamCanvas");
    if (!canvas) return;
    // Set canvas dimensions with ample vertical height for elevated loads & breakdown dimensions
    canvas.width = 850;
    canvas.height = 280;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const margin = 75;
    const beamY = 120;
    const startX = margin;
    const endX = canvas.width - margin;

    const oh = input.overhang_length || 0;
    const totalLen = input.span + oh;
    const beamLen = endX - startX;

    // Support positions
    const supportAx = startX;
    const supportBx = startX + (input.span / totalLen) * beamLen;
    const freeEndX = endX;

    // Check if UDL is present to elevate point load arrows
    const loads_arr = input.loads || [];
    const hasUDL = loads_arr.some(ld => ld.type === "udl") || input.load_type === "udl" || input.load_type === "combined";

    // ── Draw Beam Line ──
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(freeEndX, beamY);
    ctx.stroke();

    // ── Draw Supports ──
    drawSupport(ctx, supportAx, beamY, input.support_left);
    if (input.beam_type === "overhang") {
        drawSupport(ctx, supportBx, beamY, input.support_right || "roller");
    } else if (input.beam_type !== "cantilever") {
        drawSupport(ctx, freeEndX, beamY, input.support_right);
    }

    // ── Draw Support Labels ──
    ctx.fillStyle = "#10b981";
    ctx.font = "bold 13px Arial";
    ctx.textAlign = "center";
    if (oh > 0) {
        ctx.fillText("A", supportAx, beamY + 38);
        ctx.fillText("B", supportBx, beamY + 38);
        ctx.fillText("C (Free)", freeEndX, beamY + 38);
    } else {
        ctx.fillText("A", supportAx, beamY + 38);
        if (input.beam_type === "cantilever") {
            ctx.fillText("B (Free)", freeEndX, beamY + 38);
        } else {
            ctx.fillText("B", freeEndX, beamY + 38);
        }
    }

    // ── Draw Loads ──
    if (loads_arr.length > 0) {
        loads_arr.forEach(ld => {
            if (ld.type === "udl") {
                const sX = ld.start !== undefined ? startX + (ld.start / totalLen) * beamLen : startX;
                const eX = ld.end !== undefined ? startX + (ld.end / totalLen) * beamLen : freeEndX;
                drawUDL(ctx, sX, eX, beamY, ld.w);
            } else if (ld.type === "point_load") {
                const pos = ld.a !== undefined ? ld.a : input.span / 2;
                const px = startX + (pos / totalLen) * beamLen;
                const plOffset = hasUDL ? 75 : 55; // Elevate point load above UDL
                drawPointLoad(ctx, px, beamY, ld.P, plOffset);
            }
        });
    } else {
        // Legacy fallback
        if (input.load_type === "udl" || input.load_type === "combined") {
            drawUDL(ctx, startX, freeEndX, beamY, input.load);
        }
        if (input.point_load > 0 || input.load_type === "point_load") {
            const pos = input.load_position || input.span / 2;
            const px = startX + (pos / totalLen) * beamLen;
            const plVal = input.point_load > 0 ? input.point_load : input.load;
            const plOffset = (input.load > 0 && input.point_load > 0) ? 75 : 55;
            drawPointLoad(ctx, px, beamY, plVal, plOffset);
        }
    }

    // ═══════════════════════════════════════════════════
    //  SPAN LENGTH POSITION BREAKDOWN & TOTAL SPAN LINES
    // ═══════════════════════════════════════════════════
    let keypoints = [0, input.span];
    if (oh > 0) keypoints.push(totalLen);

    // Collect point load and partial UDL positions
    if (loads_arr.length > 0) {
        loads_arr.forEach(ld => {
            if (ld.type === "point_load") {
                const pos = ld.a !== undefined ? ld.a : input.span / 2;
                if (pos > 0 && pos < totalLen) keypoints.push(pos);
            } else if (ld.type === "udl") {
                if (ld.start && ld.start > 0 && ld.start < totalLen) keypoints.push(ld.start);
                if (ld.end && ld.end > 0 && ld.end < totalLen) keypoints.push(ld.end);
            }
        });
    }

    // Sort and deduplicate keypoints
    keypoints.sort((a, b) => a - b);
    let uniquePts = [];
    keypoints.forEach(pt => {
        if (!uniquePts.some(u => Math.abs(u - pt) < 0.01)) uniquePts.push(pt);
    });

    const dimY = beamY + 58;
    const tickH = 5;

    // If intermediate load positions exist, draw segment breakdown
    if (uniquePts.length > 2) {
        ctx.strokeStyle = "#94a3b8";
        ctx.lineWidth = 1.2;

        for (let j = 0; j < uniquePts.length - 1; j++) {
            const pt1 = uniquePts[j];
            const pt2 = uniquePts[j + 1];
            const x1 = startX + (pt1 / totalLen) * beamLen;
            const x2 = startX + (pt2 / totalLen) * beamLen;
            const segLen = pt2 - pt1;
            const midSegX = (x1 + x2) / 2;

            // Vertical ticks
            ctx.beginPath();
            ctx.moveTo(x1, dimY - tickH);
            ctx.lineTo(x1, dimY + tickH);
            ctx.moveTo(x2, dimY - tickH);
            ctx.lineTo(x2, dimY + tickH);
            ctx.stroke();

            // Dashed segment line
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(x1, dimY);
            ctx.lineTo(x2, dimY);
            ctx.stroke();
            ctx.setLineDash([]);

            // Segment length text
            ctx.fillStyle = "#97ad02";
            ctx.font = "11px Arial";
            ctx.textAlign = "center";
            ctx.fillText(`${segLen.toFixed(1)}m`, midSegX, dimY - 4);
        }

        // Draw Total Span Line below breakdown
        const totalDimY = dimY + 30;
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 1.5;

        // Main span total line
        ctx.beginPath();
        ctx.moveTo(supportAx, totalDimY - tickH);
        ctx.lineTo(supportAx, totalDimY + tickH);
        ctx.moveTo(supportBx, totalDimY - tickH);
        ctx.lineTo(supportBx, totalDimY + tickH);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(supportAx, totalDimY);
        ctx.lineTo(supportBx, totalDimY);
        ctx.stroke();

        ctx.fillStyle = "#f59e0b";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "center";
        ctx.fillText(`Total Span: ${input.span}m`, (supportAx + supportBx) / 2, totalDimY - 5);

        // Overhang total line if present
        if (oh > 0) {
            ctx.strokeStyle = "#ec4899";
            ctx.beginPath();
            ctx.moveTo(supportBx, totalDimY - tickH);
            ctx.lineTo(supportBx, totalDimY + tickH);
            ctx.moveTo(freeEndX, totalDimY - tickH);
            ctx.lineTo(freeEndX, totalDimY + tickH);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(supportBx, totalDimY);
            ctx.lineTo(freeEndX, totalDimY);
            ctx.stroke();

            ctx.fillStyle = "#ec4899";
            ctx.fillText(`OH: ${oh}m`, (supportBx + freeEndX) / 2, totalDimY - 5);
        }
    } else {
        // No breakdown needed — single total span line
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 1.5;

        ctx.beginPath();
        ctx.moveTo(supportAx, dimY - tickH);
        ctx.lineTo(supportAx, dimY + tickH);
        ctx.moveTo(supportBx, dimY - tickH);
        ctx.lineTo(supportBx, dimY + tickH);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(supportAx, dimY);
        ctx.lineTo(supportBx, dimY);
        ctx.stroke();

        ctx.fillStyle = "#f59e0b";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "center";
        ctx.fillText(`Span: ${input.span}m`, (supportAx + supportBx) / 2, dimY - 5);

        if (oh > 0) {
            ctx.strokeStyle = "#ec4899";
            ctx.beginPath();
            ctx.moveTo(supportBx, dimY - tickH);
            ctx.lineTo(supportBx, dimY + tickH);
            ctx.moveTo(freeEndX, dimY - tickH);
            ctx.lineTo(freeEndX, dimY + tickH);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(supportBx, dimY);
            ctx.lineTo(freeEndX, dimY);
            ctx.stroke();

            ctx.fillStyle = "#ec4899";
            ctx.fillText(`OH: ${oh}m`, (supportBx + freeEndX) / 2, dimY - 5);
        }
    }

    ctx.textAlign = "start";
}


function drawSupport(ctx, x, y, type) {
    ctx.lineWidth = 2;

    if (type === "roller") {
        ctx.strokeStyle = "#f59e0b";
        ctx.fillStyle = "transparent";
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 10, y + 18);
        ctx.lineTo(x + 10, y + 18);
        ctx.closePath();
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(x, y + 23, 5, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x - 14, y + 29);
        ctx.lineTo(x + 14, y + 29);
        ctx.stroke();

    } else if (type === "pinned") {
        ctx.strokeStyle = "#10b981";
        ctx.fillStyle = "transparent";
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 10, y + 18);
        ctx.lineTo(x + 10, y + 18);
        ctx.closePath();
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x - 14, y + 18);
        ctx.lineTo(x + 14, y + 18);
        ctx.stroke();
        for (let i = -8; i <= 8; i += 5) {
            ctx.beginPath();
            ctx.moveTo(x + i, y + 18);
            ctx.lineTo(x + i - 4, y + 24);
            ctx.stroke();
        }

    } else if (type === "fixed") {
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(x, y - 20);
        ctx.lineTo(x, y + 25);
        ctx.stroke();
        ctx.lineWidth = 1.5;
        for (let i = -15; i <= 20; i += 7) {
            ctx.beginPath();
            ctx.moveTo(x, y + i);
            ctx.lineTo(x - 10, y + i + 7);
            ctx.stroke();
        }

    } else if (type === "free") {
        // Free end
    }
}


function drawUDL(ctx, startX, endX, beamY, load) {
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;

    const udlTopY = beamY - 40;
    const arrows = Math.max(4, Math.floor((endX - startX) / 25));
    const spacing = (endX - startX) / arrows;

    // Top horizontal line
    ctx.beginPath();
    ctx.moveTo(startX, udlTopY);
    ctx.lineTo(endX, udlTopY);
    ctx.stroke();

    for (let i = 0; i <= arrows; i++) {
        let x = startX + i * spacing;

        // Vertical arrow line
        ctx.beginPath();
        ctx.moveTo(x, udlTopY);
        ctx.lineTo(x, beamY - 2);
        ctx.stroke();

        // Arrow head
        ctx.beginPath();
        ctx.moveTo(x - 3, beamY - 10);
        ctx.lineTo(x, beamY - 2);
        ctx.lineTo(x + 3, beamY - 10);
        ctx.stroke();
    }

    // UDL Load label
    ctx.fillStyle = "#10b981";
    ctx.font = "bold 11px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`${load} kN/m`, (startX + endX) / 2, udlTopY - 6);
}


function drawPointLoad(ctx, px, beamY, load, startYOffset = 55) {
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 3;

    const arrowTopY = beamY - startYOffset;

    // Arrow line (starts higher if elevated above UDL)
    ctx.beginPath();
    ctx.moveTo(px, arrowTopY);
    ctx.lineTo(px, beamY - 2);
    ctx.stroke();

    // Arrow head
    ctx.beginPath();
    ctx.moveTo(px - 6, beamY - 12);
    ctx.lineTo(px, beamY - 2);
    ctx.lineTo(px + 6, beamY - 12);
    ctx.stroke();

    // Label — placed clearly above top of arrow line
    ctx.fillStyle = "#ef4444";
    ctx.font = "bold 12px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`${load} kN`, px, arrowTopY - 5);
}


function drawTriangularLoad(ctx, startX, endX, beamY, load) {
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 2;

    const arrows = 10;
    const spacing = (endX - startX) / arrows;

    ctx.beginPath();
    ctx.moveTo(startX, beamY);
    ctx.lineTo(endX, beamY - 40);
    ctx.stroke();

    for (let i = 1; i <= arrows; i++) {
        let x = startX + i * spacing;
        let height = (i / arrows) * 40;

        ctx.beginPath();
        ctx.moveTo(x, beamY - height);
        ctx.lineTo(x, beamY);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x - 4, beamY - 8);
        ctx.lineTo(x, beamY);
        ctx.lineTo(x + 4, beamY - 8);
        ctx.stroke();
    }

    ctx.fillStyle = "#f59e0b";
    ctx.font = "12px Arial";
    ctx.fillText(`${load} kN/m (max)`, endX - 70, beamY - 45);
}


// ═══════════════════════════════════════════════
//  MULTI-SPAN CONTINUOUS BEAM DIAGRAM
// ═══════════════════════════════════════════════

function drawContinuousBeamDiagram(contData, loadValue) {
    const canvas = document.getElementById("beamCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const totalLength = contData.spans.reduce((a, b) => a + b, 0);
    canvas.width = Math.max(850, 150 + contData.spans.length * 220);
    canvas.height = 320;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const marginL = 75;
    const marginR = 75;
    const beamY = 135;
    const usableW = canvas.width - marginL - marginR;

    // Scale: pixels per meter
    const scale = usableW / totalLength;
    const beamEndX = marginL + totalLength * scale;

    // ── Draw per-span load arrows ──
    const spanLoads = contData.span_loads || [];
    let spanStartX = marginL;

    for (let i = 0; i < contData.spans.length; i++) {
        const spanPx = contData.spans[i] * scale;
        const spanEndX = spanStartX + spanPx;

        let ldList = spanLoads[i] || [];
        if (!Array.isArray(ldList)) ldList = [ldList];

        let userUDLs = ldList.filter(ld => ld.type === "udl" && !ld.is_dead);
        let hasUDL = userUDLs.length > 0;
        let udlTotal = userUDLs.reduce((sum, ld) => sum + (ld.w || 0), 0);
        let plCount = 0;

        // Draw point loads — elevated if span has UDL
        for (const ld of ldList) {
            if (ld.type === "point_load") {
                const aMetres = ld.a || (contData.spans[i] / 2);
                const px = spanStartX + (aMetres / contData.spans[i]) * spanPx;
                const plOffset = hasUDL ? 75 : 55; // Elevate above UDL line (beamY - 75 vs beamY - 40)
                const arrowTopY = beamY - plOffset;

                ctx.strokeStyle = "#ef4444";
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(px, arrowTopY);
                ctx.lineTo(px, beamY - 2);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(px - 5, beamY - 12);
                ctx.lineTo(px, beamY - 2);
                ctx.lineTo(px + 5, beamY - 12);
                ctx.stroke();

                // Point load value raised above UDL text
                ctx.fillStyle = "#ef4444";
                ctx.font = "bold 12px Arial";
                ctx.textAlign = "center";
                ctx.fillText(`${ld.P} kN`, px, arrowTopY - 6 - (plCount * 14));
                plCount++;
            }
        }

        // Draw UDL arrows for this span if a user-applied UDL is present
        if (hasUDL) {
            const udlTopY = beamY - 40;
            let uStartMetres = 0;
            let uEndMetres = contData.spans[i];
            const firstUserUDL = userUDLs[0];

            const cumSpanStart = contData.spans.slice(0, i).reduce((a, b) => a + b, 0);
            const cumSpanEnd = cumSpanStart + contData.spans[i];

            if (firstUserUDL.start !== undefined && firstUserUDL.end !== undefined) {
                const globalStart = Math.max(cumSpanStart, firstUserUDL.start);
                const globalEnd = Math.min(cumSpanEnd, firstUserUDL.end);
                uStartMetres = Math.max(0, globalStart - cumSpanStart);
                uEndMetres = Math.min(contData.spans[i], globalEnd - cumSpanStart);
            }

            const udlDrawStartX = spanStartX + (uStartMetres / contData.spans[i]) * spanPx;
            const udlDrawEndX = spanStartX + (uEndMetres / contData.spans[i]) * spanPx;
            const drawWidth = udlDrawEndX - udlDrawStartX;

            const arrowsInSpan = Math.max(4, Math.floor((uEndMetres - uStartMetres) * 2));
            const arrowSpacing = drawWidth / (arrowsInSpan || 1);

            ctx.strokeStyle = "#10b981";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(udlDrawStartX, udlTopY);
            ctx.lineTo(udlDrawEndX, udlTopY);
            ctx.stroke();

            for (let j = 0; j <= arrowsInSpan; j++) {
                const x = udlDrawStartX + j * arrowSpacing;
                ctx.beginPath();
                ctx.moveTo(x, udlTopY);
                ctx.lineTo(x, beamY - 2);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(x - 3, beamY - 10);
                ctx.lineTo(x, beamY - 2);
                ctx.lineTo(x + 3, beamY - 10);
                ctx.stroke();
            }

            // UDL label
            ctx.fillStyle = "#10b981";
            ctx.font = "bold 11px Arial";
            ctx.textAlign = "center";
            ctx.fillText(`${udlTotal.toFixed(1)} kN/m`, (udlDrawStartX + udlDrawEndX) / 2, udlTopY - 6);
        }

        spanStartX = spanEndX;
    }

    // ── Draw continuous beam line ──
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(marginL, beamY);
    ctx.lineTo(beamEndX, beamY);
    ctx.stroke();

    // ── Draw supports & support labels ──
    let xPos = marginL;
    ctx.lineWidth = 2;

    for (let i = 0; i < contData.supports.length; i++) {
        const supType = contData.supports[i];
        const label = String.fromCharCode(65 + i);

        if (supType === "fixed") {
            drawFixedSupport(ctx, xPos, beamY);
        } else if (supType === "roller") {
            drawRollerSupport(ctx, xPos, beamY);
        } else {
            drawPinnedSupport(ctx, xPos, beamY);
        }

        ctx.fillStyle = "#10b981";
        ctx.font = "bold 14px Arial";
        ctx.textAlign = "center";
        ctx.fillText(label, xPos, beamY + 40);

        if (i < contData.spans.length) {
            xPos += contData.spans[i] * scale;
        }
    }

    // ═══════════════════════════════════════════════════
    //  CONTINUOUS BEAM SPAN BREAKDOWN & TOTAL SPAN LINES
    // ═══════════════════════════════════════════════════
    let xLabel = marginL;
    const dimY = beamY + 58;
    const totalDimY = dimY + 30;
    const tickH = 5;

    for (let i = 0; i < contData.spans.length; i++) {
        const spanPx = contData.spans[i] * scale;
        const spanEndX = xLabel + spanPx;

        // Collect internal load keypoints for span i
        let ldList = spanLoads[i] || [];
        if (!Array.isArray(ldList)) ldList = [ldList];

        let spanPts = [0, contData.spans[i]];
        ldList.forEach(ld => {
            if (ld.type === "point_load") {
                const pos = ld.a || (contData.spans[i] / 2);
                if (pos > 0 && pos < contData.spans[i]) spanPts.push(pos);
            }
        });

        spanPts.sort((a, b) => a - b);
        let uniqueSpanPts = [];
        spanPts.forEach(pt => {
            if (!uniqueSpanPts.some(u => Math.abs(u - pt) < 0.01)) uniqueSpanPts.push(pt);
        });

        if (uniqueSpanPts.length > 2) {
            // Draw segment breakdown within span i
            ctx.strokeStyle = "#94a3b8";
            ctx.lineWidth = 1.2;

            for (let j = 0; j < uniqueSpanPts.length - 1; j++) {
                const pt1 = uniqueSpanPts[j];
                const pt2 = uniqueSpanPts[j + 1];
                const x1 = xLabel + (pt1 / contData.spans[i]) * spanPx;
                const x2 = xLabel + (pt2 / contData.spans[i]) * spanPx;
                const segLen = pt2 - pt1;

                ctx.beginPath();
                ctx.moveTo(x1, dimY - tickH);
                ctx.lineTo(x1, dimY + tickH);
                ctx.moveTo(x2, dimY - tickH);
                ctx.lineTo(x2, dimY + tickH);
                ctx.stroke();

                ctx.setLineDash([3, 3]);
                ctx.beginPath();
                ctx.moveTo(x1, dimY);
                ctx.lineTo(x2, dimY);
                ctx.stroke();
                ctx.setLineDash([]);

                ctx.fillStyle = "#97ad02";
                ctx.font = "11px Arial";
                ctx.textAlign = "center";
                ctx.fillText(`${segLen.toFixed(1)}m`, (x1 + x2) / 2, dimY - 4);
            }

            // Draw Span total line below breakdown
            ctx.strokeStyle = "#f59e0b";
            ctx.lineWidth = 1.5;

            ctx.beginPath();
            ctx.moveTo(xLabel, totalDimY - tickH);
            ctx.lineTo(xLabel, totalDimY + tickH);
            ctx.moveTo(spanEndX, totalDimY - tickH);
            ctx.lineTo(spanEndX, totalDimY + tickH);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(xLabel, totalDimY);
            ctx.lineTo(spanEndX, totalDimY);
            ctx.stroke();

            ctx.fillStyle = "#f59e0b";
            ctx.font = "bold 12px Arial";
            ctx.textAlign = "center";
            ctx.fillText(`${contData.spans[i]}m`, (xLabel + spanEndX) / 2, totalDimY - 5);
        } else {
            // Standard single span dimension line
            ctx.strokeStyle = "#f59e0b";
            ctx.lineWidth = 1.5;

            ctx.beginPath();
            ctx.moveTo(xLabel, dimY - tickH);
            ctx.lineTo(xLabel, dimY + tickH);
            ctx.moveTo(spanEndX, dimY - tickH);
            ctx.lineTo(spanEndX, dimY + tickH);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(xLabel, dimY);
            ctx.lineTo(spanEndX, dimY);
            ctx.stroke();

            ctx.fillStyle = "#f59e0b";
            ctx.font = "bold 12px Arial";
            ctx.textAlign = "center";
            ctx.fillText(`${contData.spans[i]}m`, (xLabel + spanEndX) / 2, dimY - 5);
        }

        xLabel = spanEndX;
    }

    // ── Draw Overall Total Continuous Beam Length Line at bottom ──
    const overallDimY = beamY + 118;
    ctx.strokeStyle = "#ec4899";
    ctx.lineWidth = 1.8;

    ctx.beginPath();
    ctx.moveTo(marginL, overallDimY - tickH);
    ctx.lineTo(marginL, overallDimY + tickH);
    ctx.moveTo(beamEndX, overallDimY - tickH);
    ctx.lineTo(beamEndX, overallDimY + tickH);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(marginL, overallDimY);
    ctx.lineTo(beamEndX, overallDimY);
    ctx.stroke();

    ctx.fillStyle = "#ec4899";
    ctx.font = "bold 12px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`Total Continuous Length: ${totalLength.toFixed(1)}m`, (marginL + beamEndX) / 2, overallDimY - 6);

    // ── Support moments (show non-zero) ──
    xPos = marginL;
    ctx.font = "11px Arial";
    ctx.fillStyle = "#ef4444";
    ctx.textAlign = "center";

    for (let i = 0; i < contData.support_moments.length; i++) {
        const m = contData.support_moments[i];
        if (Math.abs(m) > 0.01) {
            ctx.fillText("M=" + m.toFixed(1), xPos, beamY - 88);
        }
        if (i < contData.spans.length) {
            xPos += contData.spans[i] * scale;
        }
    }
}

function drawPinnedSupport(ctx, x, y) {
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 2;
    ctx.fillStyle = "transparent";

    // Triangle
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 12, y + 22);
    ctx.lineTo(x + 12, y + 22);
    ctx.closePath();
    ctx.stroke();

    // Ground line under triangle
    ctx.beginPath();
    ctx.moveTo(x - 16, y + 25);
    ctx.lineTo(x + 16, y + 25);
    ctx.stroke();

    // Small hatching lines under ground
    for (let i = -12; i <= 12; i += 6) {
        ctx.beginPath();
        ctx.moveTo(x + i, y + 25);
        ctx.lineTo(x + i - 4, y + 30);
        ctx.stroke();
    }
}

function drawRollerSupport(ctx, x, y) {
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 2;
    ctx.fillStyle = "transparent";

    // Triangle
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 12, y + 18);
    ctx.lineTo(x + 12, y + 18);
    ctx.closePath();
    ctx.stroke();

    // Circle (roller) underneath
    ctx.beginPath();
    ctx.arc(x, y + 24, 5, 0, Math.PI * 2);
    ctx.stroke();

    // Ground line under circle
    ctx.beginPath();
    ctx.moveTo(x - 16, y + 30);
    ctx.lineTo(x + 16, y + 30);
    ctx.stroke();
}

function drawFixedSupport(ctx, x, y) {
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 3;

    // Vertical wall
    ctx.beginPath();
    ctx.moveTo(x, y - 20);
    ctx.lineTo(x, y + 25);
    ctx.stroke();

    // Hatching lines
    ctx.lineWidth = 1.5;
    for (let i = -15; i <= 20; i += 7) {
        ctx.beginPath();
        ctx.moveTo(x, y + i);
        ctx.lineTo(x - 10, y + i + 7);
        ctx.stroke();
    }
}

// ═══════════════════════════════════════════════
//  DOWNLOAD MODAL & PDF FUNCTIONS
// ═══════════════════════════════════════════════

let lastDesignData = null; // Store last API response for downloads

function openDownloadModal() {
    document.getElementById("downloadModal").classList.add("active");
}

function closeDownloadModal() {
    document.getElementById("downloadModal").classList.remove("active");
}

async function downloadResults() {
    const projectTitle = document.getElementById("projectTitleInput").value.trim();
    closeDownloadModal();

    // Build a comprehensive data payload from whatever is on screen
    const payload = lastDesignData;

    if (!payload) {
        alert("No design results available. Please generate a design first.");
        return;
    }
    payload.project_title = projectTitle;

    // ── Capture diagram canvases as base64 PNG ──
    const diagrams = {};

    const beamCanvas = document.getElementById("beamCanvas");
    if (beamCanvas && beamCanvas.width > 0 && beamCanvas.height > 0) {
        diagrams.beam_diagram = beamCanvas.toDataURL("image/png");
    }

    // Chart.js canvases
    const chartIds = ["loadChart", "shearChart", "momentChart"];
    const chartKeys = ["load_diagram", "shear_diagram", "moment_diagram"];
    for (let i = 0; i < chartIds.length; i++) {
        const c = document.getElementById(chartIds[i]);
        if (c && c.width > 0 && c.height > 0) {
            diagrams[chartKeys[i]] = c.toDataURL("image/png");
        }
    }

    payload.diagrams_base64 = diagrams;

    try {
        const response = await fetch("/download-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            alert("Failed to generate PDF.");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "ai-rcbds_results_report.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error("Download error:", err);
        alert("Error downloading results.");
    }
}

async function downloadCalculationSheet() {
    const projectTitle = document.getElementById("projectTitleInput").value.trim();
    closeDownloadModal();

    const payload = lastDesignData;
    if (!payload) {
        alert("No design results available. Please generate a design first.");
        return;
    }
    payload.project_title = projectTitle;

    // Capture diagram canvases as base64 PNG (same as downloadResults)
    const diagrams = {};
    const beamCanvas = document.getElementById("beamCanvas");
    if (beamCanvas && beamCanvas.width > 0 && beamCanvas.height > 0) {
        diagrams.beam_diagram = beamCanvas.toDataURL("image/png");
    }
    const chartIds = ["loadChart", "shearChart", "momentChart"];
    const chartKeys = ["load_diagram", "shear_diagram", "moment_diagram"];
    for (let i = 0; i < chartIds.length; i++) {
        const c = document.getElementById(chartIds[i]);
        if (c && c.width > 0 && c.height > 0) {
            diagrams[chartKeys[i]] = c.toDataURL("image/png");
        }
    }
    payload.diagrams_base64 = diagrams;

    try {
        const response = await fetch("/download-calculation-sheet", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            alert(err.error || "Failed to generate calculation sheet.");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "ai-rcbds_calc_sheet.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error("Calc sheet error:", err);
        alert("Error generating calculation sheet.");
    }
}

async function checkHealth() {
    const res = await fetch("/health");
    const data = await res.json();

    document.getElementById("status").innerText = data.status.toUpperCase();
}

checkHealth();
