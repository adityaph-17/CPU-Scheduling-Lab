/**
 * static/script.js
 * Frontend controller for CPU Scheduling Lab.
 * Comprehensive DSA platform supporting all 6 scheduling algorithms:
 * - Preemptive: Round Robin (FIFO Queue), SRTF (Min-Heap), Priority (Min-Heap)
 * - Non-Preemptive: FCFS (FIFO Queue), SJF (Min-Heap), Priority (Min-Heap)
 * - Dynamic data structure visualizations (Binary Tree, Array Memory, FIFO Queue)
 * - Performance analysis & All-6-algorithm comparison table
 * - Zero automatic scrolling on simulation updates
 */

document.addEventListener("DOMContentLoaded", () => {
    // =========================================================================
    // 1. ALGORITHM ENCYCLOPEDIA & METADATA
    // =========================================================================
    const ALGORITHM_DATA = {
        round_robin: {
            name: "Round Robin (RR)",
            category: "Preemptive",
            dataStructure: "FIFO Ready Queue",
            description: "Gives each ready process a fixed time slice called a time quantum. Unfinished processes return to the end of the FIFO ready queue.",
            selectionRule: "Dispatches the process at the head of the FIFO ready queue. If it does not finish within the time quantum (Q), it is interrupted and placed at the tail.",
            complexity: "O(1) per scheduling decision (Enqueue & Dequeue at queue ends).",
            advantages: "Fair allocation of CPU; prevents starvation; ideal for time-sharing operating systems.",
            limitations: "High context-switching overhead if quantum is too small; degenerates into FCFS if quantum is very large.",
            example: "Processes P1(5) and P2(3) with Q=2: P1 runs [0-2], P2 runs [2-4], P1 runs [4-6], P2 finishes [6-7], P1 finishes [7-8].",
            tieBreaker: "When a time slice expires at the same tick a new process arrives, new arrivals enter the queue first, followed by the expiring process."
        },
        srtf: {
            name: "Shortest Remaining Time First (SRTF)",
            category: "Preemptive",
            dataStructure: "Binary Min-Heap (Key: Remaining Execution Time)",
            description: "Selects the ready process with the shortest remaining execution time. A running process can be interrupted when another process has a shorter remaining time.",
            selectionRule: "Continuously selects the process with the shortest remaining time from the Min-Heap. Arriving processes with strictly less remaining time preempt the CPU.",
            complexity: "O(log N) insertion and extraction using binary min-heap.",
            advantages: "Minimizes average waiting time across all preemptive scheduling algorithms.",
            limitations: "Long processes can suffer from starvation; burst times must be known or estimated in advance.",
            example: "P1(AT=0, BT=8). At T=1, P2(AT=1, BT=4) arrives. P2 has remaining 4 < P1's 7, so P2 preempts P1 immediately.",
            tieBreaker: "Earlier arrival time; if arrival times are identical, natural numeric Process ID (e.g., P2 before P10)."
        },
        priority_preemptive: {
            name: "Preemptive Priority Scheduling",
            category: "Preemptive",
            dataStructure: "Binary Min-Heap (Key: Priority)",
            description: "Selects the highest-priority ready process. A running process can be interrupted when a higher-priority process arrives.",
            selectionRule: "Selects the process with the highest priority (lowest numerical value) from the Min-Heap. An arriving higher-priority task preempts the running process.",
            complexity: "O(log N) insertion and root extraction via Min-Heap.",
            advantages: "Important system tasks and high-priority processes receive immediate CPU attention.",
            limitations: "Indefinite blocking (starvation) of low-priority processes unless an aging technique is applied.",
            example: "P1(Priority 2) is running. At T=1, P2(Priority 1) arrives. Because 1 < 2, P2 immediately preempts P1.",
            tieBreaker: "Earlier arrival time; if arrival times are identical, natural numeric Process ID (e.g., P2 before P10)."
        },
        fcfs: {
            name: "First-Come, First-Served (FCFS)",
            category: "Non-Preemptive",
            dataStructure: "FIFO Ready Queue",
            description: "Executes processes in arrival order. Once a process starts, it runs until completion.",
            selectionRule: "Executes processes strictly in the order they arrive in the ready queue. Runs uninterrupted until completion.",
            complexity: "O(1) process selection from queue head.",
            advantages: "Simple to understand and implement; zero preemption overhead.",
            limitations: "Susceptible to the Convoy Effect (short processes stuck waiting behind long CPU-bound tasks), causing high average waiting time.",
            example: "P1(BT=10) arrives at T=0; P2(BT=2) arrives at T=1. P2 must wait 9 units until P1 finishes at T=10.",
            tieBreaker: "Order of arrival time; if arrival times are identical, natural numeric Process ID (e.g., P2 before P10)."
        },
        sjf: {
            name: "Shortest Job First (SJF)",
            category: "Non-Preemptive",
            dataStructure: "Binary Min-Heap (Key: Initial Burst Time)",
            description: "Selects the ready process with the shortest original burst time. The selected process runs until completion.",
            selectionRule: "When the CPU becomes free, the ready process with the smallest initial burst time is chosen from the Min-Heap and runs to completion.",
            complexity: "O(log N) process insertion and extraction via Min-Heap.",
            advantages: "Proven to provide the optimal (minimum) average waiting time among all non-preemptive algorithms.",
            limitations: "Cannot preempt long jobs once started; long processes may starve if short jobs continually arrive.",
            example: "At T=2, CPU finishes. Ready processes are P1(BT=6) and P2(BT=3). SJF selects P2 first.",
            tieBreaker: "Earlier arrival time; if arrival times are identical, natural numeric Process ID (e.g., P2 before P10)."
        },
        priority_non_preemptive: {
            name: "Non-Preemptive Priority Scheduling",
            category: "Non-Preemptive",
            dataStructure: "Binary Min-Heap (Key: Priority)",
            description: "Selects the highest-priority ready process. Once started, that process runs until completion.",
            selectionRule: "When the CPU is free, selects the ready process with the highest priority (lowest numerical value) from the Min-Heap and runs it to completion.",
            complexity: "O(log N) insertion and extraction via Min-Heap.",
            advantages: "Simple priority-driven scheduling without the overhead of saving and restoring preempted process registers.",
            limitations: "A high-priority process must wait if a low-priority process is currently executing; risk of starvation.",
            example: "P1(Priority 3) starts at T=0. At T=1, P2(Priority 1) arrives. P1 continues until completion before P2 can run.",
            tieBreaker: "Earlier arrival time; if arrival times are identical, natural numeric Process ID (e.g., P2 before P10)."
        }
    };

    // =========================================================================
    // 2. STATE MANAGEMENT
    // =========================================================================
    const state = {
        processes: [
            { pid: "P1", arrival_time: 0, burst_time: 5, priority: 2, color: "#3b82f6" },
            { pid: "P2", arrival_time: 1, burst_time: 4, priority: 1, color: "#ec4899" },
            { pid: "P3", arrival_time: 2, burst_time: 2, priority: 3, color: "#10b981" },
            { pid: "P4", arrival_time: 3, burst_time: 1, priority: 4, color: "#f59e0b" }
        ],
        algorithm: "priority_preemptive",
        quantum: 2,
        simulationData: null,
        currentTime: 0,
        isPlaying: false,
        playbackTimer: null,
        playbackSpeed: 800,
        heapViewMode: "tree" // 'tree' or 'array'
    };

    const colorPalette = [
        "#3b82f6", "#ec4899", "#10b981", "#f59e0b",
        "#06b6d4", "#8b5cf6", "#f43f5e", "#14b8a6", "#6366f1"
    ];

    // =========================================================================
    // 3. DOM REFERENCES
    // =========================================================================
    const elements = {
        // Theme & Mobile Nav
        themeToggleBtn: document.getElementById("themeToggleBtn"),
        themeLabel: document.getElementById("themeLabel"),
        mobileMenuBtn: document.getElementById("mobileMenuBtn"),
        siteNav: document.getElementById("siteNav"),
        currentYearSpan: document.getElementById("currentYearSpan"),

        // Alert
        errorBanner: document.getElementById("errorBanner"),
        errorMessageText: document.getElementById("errorMessageText"),
        errorCloseBtn: document.getElementById("errorCloseBtn"),

        // Setup & Algorithm Radios
        presetSelect: document.getElementById("presetSelect"),
        algoRadios: document.querySelectorAll("input[name='algorithm']"),
        quantumControlWrap: document.getElementById("quantumControlWrap"),
        inputQuantum: document.getElementById("inputQuantum"),
        priorityRuleNote: document.getElementById("priorityRuleNote"),

        // Phase 6 Immediate Algorithm Display Elements
        activeAlgoBadge: document.getElementById("activeAlgoBadge"),
        activeAlgoTitle: document.getElementById("activeAlgoTitle"),
        activeAlgoDs: document.getElementById("activeAlgoDs"),
        activeAlgoDescription: document.getElementById("activeAlgoDescription"),
        activeAlgoQuantumStrip: document.getElementById("activeAlgoQuantumStrip"),
        activeAlgoQuantumVal: document.getElementById("activeAlgoQuantumVal"),
        activeAlgoPriorityStrip: document.getElementById("activeAlgoPriorityStrip"),

        // Process Form & Setup Actions
        addProcessForm: document.getElementById("addProcessForm"),
        inputPid: document.getElementById("inputPid"),
        inputArrival: document.getElementById("inputArrival"),
        inputBurst: document.getElementById("inputBurst"),
        inputPriority: document.getElementById("inputPriority"),
        inputColor: document.getElementById("inputColor"),
        processTableBody: document.getElementById("processTableBody"),
        btnRunSimulation: document.getElementById("btnRunSimulation"),
        btnCompareAll: document.getElementById("btnCompareAll"),
        btnQuickAdd: document.getElementById("btnQuickAdd"),
        btnResetProcesses: document.getElementById("btnResetProcesses"),
        processCountBadge: document.getElementById("processCountBadge"),

        // Algorithm Information Section
        algoInfoContent: document.getElementById("algoInfoContent"),

        // Simulation Area
        currentTimeDisplay: document.getElementById("currentTimeDisplay"),
        totalTimeDisplay: document.getElementById("totalTimeDisplay"),
        btnReset: document.getElementById("btnReset"),
        btnStepPrev: document.getElementById("btnStepPrev"),
        btnPlayPause: document.getElementById("btnPlayPause"),
        playText: document.getElementById("playText"),
        btnStepNext: document.getElementById("btnStepNext"),
        btnJumpEnd: document.getElementById("btnJumpEnd"),
        speedSelect: document.getElementById("speedSelect"),
        timelineScrubber: document.getElementById("timelineScrubber"),

        // Decision Callout & CPU State
        eventTimeTag: document.getElementById("eventTimeTag"),
        cpuStatusBadge: document.getElementById("cpuStatusBadge"),
        eventCalloutText: document.getElementById("eventCalloutText"),

        // Gantt Chart
        ganttLegend: document.getElementById("ganttLegend"),
        ganttWrapper: document.getElementById("ganttWrapper"),
        ganttTrack: document.getElementById("ganttTrack"),
        ganttAxis: document.getElementById("ganttAxis"),
        ganttPlayhead: document.getElementById("ganttPlayhead"),
        playheadTag: document.getElementById("playheadTag"),

        // Live Lifecycle Table
        statusTimeBadge: document.getElementById("statusTimeBadge"),
        lifecycleTableBody: document.getElementById("lifecycleTableBody"),

        // DSA Visualization Area
        dsaActiveContainer: document.getElementById("dsaActiveContainer"),

        // Performance Metrics
        kpiTat: document.getElementById("kpiTat"),
        kpiWt: document.getElementById("kpiWt"),
        kpiRt: document.getElementById("kpiRt"),
        kpiCpuUtil: document.getElementById("kpiCpuUtil"),
        kpiThroughput: document.getElementById("kpiThroughput"),
        metricsTableBody: document.getElementById("metricsTableBody"),
        comparisonTableBody: document.getElementById("comparisonTableBody"),

        // Event Log
        eventsLogContainer: document.getElementById("eventsLogContainer"),
        logCountBadge: document.getElementById("logCountBadge")
    };

    // =========================================================================
    // 4. INITIALIZATION
    // =========================================================================
    function init() {
        setupTheme();
        if (elements.currentYearSpan) {
            elements.currentYearSpan.textContent = new Date().getFullYear();
        }
        renderProcessTable();
        updateAlgorithmView(state.algorithm);
        setupEventListeners();
        runSimulation();
    }

    function setupEventListeners() {
        // Theme
        if (elements.themeToggleBtn) {
            elements.themeToggleBtn.addEventListener("click", toggleTheme);
        }

        // Mobile Nav
        if (elements.mobileMenuBtn && elements.siteNav) {
            elements.mobileMenuBtn.addEventListener("click", () => {
                elements.siteNav.classList.toggle("mobile-open");
            });
        }

        // Close mobile nav on click
        document.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", () => {
                if (elements.siteNav) {
                    elements.siteNav.classList.remove("mobile-open");
                }
            });
        });

        // Algorithm Radio Selection
        if (elements.algoRadios) {
            elements.algoRadios.forEach(radio => {
                radio.addEventListener("change", (e) => {
                    state.algorithm = e.target.value;
                    updateAlgorithmView(state.algorithm);
                    runSimulation();
                });
            });
        }

        // Quantum input change
        if (elements.inputQuantum) {
            elements.inputQuantum.addEventListener("change", (e) => {
                state.quantum = Math.max(1, parseInt(e.target.value, 10) || 2);
                if (elements.activeAlgoQuantumVal) {
                    elements.activeAlgoQuantumVal.textContent = `Q = ${state.quantum} units per CPU slice`;
                }
                if (state.algorithm === "round_robin") {
                    runSimulation();
                }
            });
        }

        // Preset selector (guarded so commenting out in HTML never throws)
        if (elements.presetSelect) {
            elements.presetSelect.addEventListener("change", handlePresetSelection);
        }

        // Process Form & Actions
        if (elements.addProcessForm) {
            elements.addProcessForm.addEventListener("submit", handleAddProcess);
        }
        if (elements.btnQuickAdd) {
            elements.btnQuickAdd.addEventListener("click", handleQuickAdd);
        }
        if (elements.btnResetProcesses) {
            elements.btnResetProcesses.addEventListener("click", resetProcessList);
        }
        if (elements.btnRunSimulation) {
            elements.btnRunSimulation.addEventListener("click", () => {
                runSimulation({ scrollToSimulation: true });
            });
        }
        if (elements.btnCompareAll) {
            elements.btnCompareAll.addEventListener("click", () => {
                runComparison({ scrollToComparison: true });
            });
        }
        if (elements.errorCloseBtn) {
            elements.errorCloseBtn.addEventListener("click", hideError);
        }

        // Tab click listeners on Section 5: Algorithm Reference & Theory
        document.querySelectorAll(".algo-tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const algoKey = btn.getAttribute("data-algo");
                if (algoKey && ALGORITHM_DATA[algoKey]) {
                    renderAlgoInfoSection(algoKey);
                }
            });
        });

        // Playback Controls
        if (elements.btnPlayPause) {
            elements.btnPlayPause.addEventListener("click", togglePlayPause);
        }
        if (elements.btnReset) {
            elements.btnReset.addEventListener("click", resetPlayback);
        }
        if (elements.btnStepNext) {
            elements.btnStepNext.addEventListener("click", stepForward);
        }
        if (elements.btnStepPrev) {
            elements.btnStepPrev.addEventListener("click", stepBackward);
        }
        if (elements.btnJumpEnd) {
            elements.btnJumpEnd.addEventListener("click", jumpToEnd);
        }

        if (elements.speedSelect) {
            elements.speedSelect.addEventListener("change", (e) => {
                state.playbackSpeed = parseInt(e.target.value, 10);
                if (state.isPlaying) {
                    pauseSimulation();
                    startSimulation();
                }
            });
        }

        if (elements.timelineScrubber) {
            elements.timelineScrubber.addEventListener("input", (e) => {
                const time = parseInt(e.target.value, 10);
                pauseSimulation();
                goToTime(time);
            });
        }

        // Gantt Chart click scrubbing (never causes page jump)
        if (elements.ganttWrapper) {
            elements.ganttWrapper.addEventListener("click", handleGanttClick);
        }
    }

    // =========================================================================
    // 5. THEME TOGGLE
    // =========================================================================
    function setupTheme() {
        const savedTheme = localStorage.getItem("cpu_lab_theme") || "dark";
        if (savedTheme === "light") {
            document.body.classList.remove("dark-theme");
            document.body.classList.add("light-theme");
            elements.themeLabel.textContent = "Dark Mode";
        } else {
            document.body.classList.remove("light-theme");
            document.body.classList.add("dark-theme");
            elements.themeLabel.textContent = "Light Mode";
        }
    }

    function toggleTheme() {
        if (document.body.classList.contains("dark-theme")) {
            document.body.classList.remove("dark-theme");
            document.body.classList.add("light-theme");
            elements.themeLabel.textContent = "Dark Mode";
            localStorage.setItem("cpu_lab_theme", "light");
        } else {
            document.body.classList.remove("light-theme");
            document.body.classList.add("dark-theme");
            elements.themeLabel.textContent = "Light Mode";
            localStorage.setItem("cpu_lab_theme", "dark");
        }
    }

    // =========================================================================
    // 6. ALGORITHM VIEW UPDATER (EXPLANATION & CONTROLS)
    // =========================================================================
    function updateAlgorithmView(algoKey) {
        const info = ALGORITHM_DATA[algoKey] || ALGORITHM_DATA.priority_preemptive;

        // Update Phase 6 Immediate Algorithm Selection Card (Below Selection Field)
        if (elements.activeAlgoBadge) {
            elements.activeAlgoBadge.textContent = info.category;
            elements.activeAlgoBadge.className = `badge-pill ${info.category === 'Preemptive' ? 'badge-preempt' : 'badge-nonpreempt'}`;
        }
        if (elements.activeAlgoTitle) {
            elements.activeAlgoTitle.textContent = info.name;
        }
        if (elements.activeAlgoDs) {
            elements.activeAlgoDs.textContent = `Data Structure: ${info.dataStructure}`;
        }
        if (elements.activeAlgoDescription) {
            elements.activeAlgoDescription.textContent = info.description;
        }
        if (elements.activeAlgoQuantumStrip) {
            if (algoKey === "round_robin") {
                elements.activeAlgoQuantumStrip.classList.remove("hidden");
                if (elements.activeAlgoQuantumVal) {
                    elements.activeAlgoQuantumVal.textContent = `Q = ${state.quantum} units per CPU slice`;
                }
            } else {
                elements.activeAlgoQuantumStrip.classList.add("hidden");
            }
        }
        if (elements.activeAlgoPriorityStrip) {
            if (algoKey.includes("priority")) {
                elements.activeAlgoPriorityStrip.classList.remove("hidden");
            } else {
                elements.activeAlgoPriorityStrip.classList.add("hidden");
            }
        }

        // Toggle Time Quantum controls in parameters banner
        if (algoKey === "round_robin") {
            elements.quantumControlWrap.classList.remove("hidden");
        } else {
            elements.quantumControlWrap.classList.add("hidden");
        }

        // Toggle Priority rule note in parameters banner
        if (algoKey.includes("priority")) {
            elements.priorityRuleNote.classList.remove("hidden");
        } else {
            elements.priorityRuleNote.classList.add("hidden");
        }

        // Update Detailed Algorithm Reference Section
        renderAlgoInfoSection(algoKey);
    }

    function renderAlgoInfoSection(algoKey) {
        if (!elements.algoInfoContent) return;
        const info = ALGORITHM_DATA[algoKey];
        if (!info) return;

        // Sync tab buttons active class
        document.querySelectorAll(".algo-tab-btn").forEach(btn => {
            if (btn.getAttribute("data-algo") === algoKey) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        elements.algoInfoContent.innerHTML = `
            <div class="algo-info-header">
                <span class="algo-info-title">${escapeHtml(info.name)}</span>
                <div class="algo-info-badges">
                    <span class="badge-pill ${info.category === 'Preemptive' ? 'badge-preempt' : 'badge-nonpreempt'}">
                        ${info.category}
                    </span>
                    <span class="badge-pill badge-ds">
                        Data Structure: ${escapeHtml(info.dataStructure)}
                    </span>
                </div>
            </div>

            <div class="algo-info-grid">
                <div class="info-item" style="grid-column: 1 / -1;">
                    <span class="info-item-title">Algorithm Summary &amp; Principle</span>
                    <p class="info-item-text" style="font-weight: 600; color: var(--text-primary);">${escapeHtml(info.description)}</p>
                </div>
                <div class="info-item">
                    <span class="info-item-title">Process Selection Rule</span>
                    <p class="info-item-text">${escapeHtml(info.selectionRule)}</p>
                </div>
                <div class="info-item">
                    <span class="info-item-title">Time Complexity</span>
                    <p class="info-item-text"><code>${escapeHtml(info.complexity)}</code></p>
                </div>
                <div class="info-item">
                    <span class="info-item-title">Key Advantages</span>
                    <p class="info-item-text">${escapeHtml(info.advantages)}</p>
                </div>
                <div class="info-item">
                    <span class="info-item-title">Known Trade-offs &amp; Limitations</span>
                    <p class="info-item-text">${escapeHtml(info.limitations)}</p>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <span class="info-item-title">Concrete Execution Example</span>
                    <p class="info-item-text">${escapeHtml(info.example)}</p>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <span class="info-item-title">Deterministic Tie-Breaking Rule</span>
                    <p class="info-item-text">${escapeHtml(info.tieBreaker)}</p>
                </div>
            </div>
        `;
    }

    // =========================================================================
    // 7. PROCESS SETUP
    // =========================================================================
    function renderProcessTable() {
        elements.processTableBody.innerHTML = "";
        elements.processCountBadge.textContent = `${state.processes.length} Processes`;

        state.processes.forEach((proc, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><span class="color-dot" style="background-color: ${proc.color};"></span></td>
                <td><strong>${escapeHtml(proc.pid)}</strong></td>
                <td>${proc.arrival_time}</td>
                <td>${proc.burst_time}</td>
                <td>${proc.priority}</td>
                <td style="text-align: center;">
                    <button type="button" class="btn-remove-proc" data-index="${index}" title="Remove process">
                        Remove
                    </button>
                </td>
            `;
            elements.processTableBody.appendChild(tr);
        });

        // Attach listeners
        elements.processTableBody.querySelectorAll(".btn-remove-proc").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const idx = parseInt(e.currentTarget.getAttribute("data-index"), 10);
                if (state.processes.length <= 1) {
                    showError("Simulation requires at least 1 process.");
                    return;
                }
                state.processes.splice(idx, 1);
                renderProcessTable();
                runSimulation();
            });
        });
    }

    function handleAddProcess(e) {
        e.preventDefault();
        hideError();

        const pid = elements.inputPid.value.trim().toUpperCase();
        const arrival = parseInt(elements.inputArrival.value, 10);
        const burst = parseInt(elements.inputBurst.value, 10);
        const priority = parseInt(elements.inputPriority.value, 10);
        const color = elements.inputColor.value;

        if (!pid) {
            showError("Process ID cannot be empty.");
            return;
        }

        if (state.processes.some(p => p.pid === pid)) {
            showError(`Process ID '${pid}' already exists. Use a unique Process ID.`);
            return;
        }

        if (isNaN(arrival) || arrival < 0) {
            showError("Arrival Time must be an integer >= 0.");
            return;
        }

        if (isNaN(burst) || burst < 1) {
            showError("Burst Time must be an integer >= 1.");
            return;
        }

        if (isNaN(priority)) {
            showError("Priority must be a valid integer.");
            return;
        }

        state.processes.push({ pid, arrival_time: arrival, burst_time: burst, priority, color });
        renderProcessTable();
        runSimulation();

        // Increment for next input
        const nextNum = state.processes.length + 1;
        elements.inputPid.value = `P${nextNum}`;
        elements.inputColor.value = colorPalette[state.processes.length % colorPalette.length];
    }

    function handleQuickAdd() {
        hideError();
        const nextNum = state.processes.length + 1;
        const pid = `P${nextNum}`;
        const arrival = Math.max(0, state.processes.length - 1);
        const burst = Math.floor(Math.random() * 4) + 2;
        const priority = Math.floor(Math.random() * 5) + 1;
        const color = colorPalette[(nextNum - 1) % colorPalette.length];

        state.processes.push({ pid, arrival_time: arrival, burst_time: burst, priority, color });
        renderProcessTable();
        runSimulation();
    }

    function resetProcessList() {
        state.processes = [
            { pid: "P1", arrival_time: 0, burst_time: 5, priority: 2, color: "#3b82f6" },
            { pid: "P2", arrival_time: 1, burst_time: 4, priority: 1, color: "#ec4899" },
            { pid: "P3", arrival_time: 2, burst_time: 2, priority: 3, color: "#10b981" },
            { pid: "P4", arrival_time: 3, burst_time: 1, priority: 4, color: "#f59e0b" }
        ];
        renderProcessTable();
        runSimulation();
    }

    function handlePresetSelection(e) {
        const presetKey = e.target.value;
        if (!presetKey) return;

        fetch("/api/presets")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.presets[presetKey]) {
                    const preset = data.presets[presetKey];
                    state.processes = JSON.parse(JSON.stringify(preset.processes));
                    state.algorithm = preset.algorithm;
                    state.quantum = preset.quantum || 2;
                    elements.inputQuantum.value = state.quantum;

                    // Update active radio button
                    const targetRadio = document.querySelector(`input[name='algorithm'][value='${preset.algorithm}']`);
                    if (targetRadio) {
                        targetRadio.checked = true;
                    }

                    updateAlgorithmView(state.algorithm);
                    renderProcessTable();
                    runSimulation();
                }
            })
            .catch(err => showError("Failed to load preset: " + err.message));
    }

    // =========================================================================
    // 8. SIMULATION EXECUTION (FLASK BACKEND)
    // =========================================================================
    async function runSimulation(options = {}) {
        const shouldScroll = options && options.scrollToSimulation === true;
        hideError();
        pauseSimulation();

        const btn = elements.btnRunSimulation;
        let originalHtml = "";
        if (btn) {
            originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `<span class="btn-spinner"></span> Simulating...`;
        }

        try {
            const payload = {
                algorithm: state.algorithm,
                processes: state.processes,
                quantum: state.quantum
            };

            const response = await fetch("/api/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!result.success) {
                showError(result.error || "Simulation error.");
                return;
            }

            state.simulationData = result.data;
            setupSimulationDisplay();
            goToTime(0);

            // If user clicked the Run Simulation button, smoothly direct them to the Simulation & Gantt section
            if (shouldScroll) {
                const target = document.getElementById("simulationSection");
                if (target) {
                    target.scrollIntoView({ behavior: "smooth", block: "start" });
                    highlightSection(target);
                }
            }

            // Also trigger a background comparison update
            runComparisonBackground();

        } catch (err) {
            showError("Network or server connection error: " + err.message);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalHtml || "Run Simulation";
            }
        }
    }

    function setupSimulationDisplay() {
        const data = state.simulationData;
        const total = data.total_time;

        elements.totalTimeDisplay.textContent = total;
        elements.timelineScrubber.max = total;
        elements.timelineScrubber.value = 0;

        renderGanttChart(data.gantt_chart, total);
        renderMetrics(data);
        renderFullEventLog(data.events_log);
    }

    // =========================================================================
    // 9. ALL-6 ALGORITHM COMPARISON
    // =========================================================================
    async function runComparison(options = {}) {
        const shouldScroll = options && options.scrollToComparison === true;
        hideError();

        const btn = elements.btnCompareAll;
        let originalHtml = "";
        if (btn) {
            originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `<span class="btn-spinner"></span> Comparing...`;
        }

        try {
            const payload = {
                processes: state.processes,
                quantum: state.quantum
            };

            const response = await fetch("/api/compare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!result.success) {
                showError(result.error || "Comparison error: unable to evaluate algorithms.");
                return;
            }

            if (result.comparison) {
                renderComparisonTable(result.comparison);

                // If user clicked Compare All 6, smoothly direct them to the Comparison table section
                if (shouldScroll) {
                    const target = document.getElementById("comparisonWrapper") || document.getElementById("resultsSection");
                    if (target) {
                        target.scrollIntoView({ behavior: "smooth", block: "start" });
                        highlightSection(target);
                    }
                }
            }
        } catch (err) {
            showError("Comparison error: " + err.message);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalHtml || "Compare All 6 Algorithms";
            }
        }
    }

    function highlightSection(el) {
        if (!el) return;
        el.classList.remove("section-highlight-glow");
        void el.offsetWidth; // force DOM reflow
        el.classList.add("section-highlight-glow");
        setTimeout(() => {
            el.classList.remove("section-highlight-glow");
        }, 1800);
    }

    function runComparisonBackground() {
        fetch("/api/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ processes: state.processes, quantum: state.quantum })
        })
        .then(res => res.json())
        .then(res => {
            if (res.success && res.comparison) {
                renderComparisonTable(res.comparison);
            }
        })
        .catch(() => {});
    }

    function renderComparisonTable(comparisonList) {
        elements.comparisonTableBody.innerHTML = "";
        comparisonList.forEach(item => {
            const tr = document.createElement("tr");
            const isCurrent = item.algorithm_key === state.algorithm;
            if (isCurrent) {
                tr.style.backgroundColor = "rgba(59, 130, 246, 0.08)";
            }

            tr.innerHTML = `
                <td>
                    <strong>${escapeHtml(item.name)}</strong>
                    ${isCurrent ? '<span style="color:var(--brand-primary); font-size:11px; margin-left:6px;">(Active)</span>' : ''}
                </td>
                <td>${escapeHtml(item.category)}</td>
                <td><code>${escapeHtml(item.data_structure)}</code></td>
                <td><strong>${item.avg_turnaround_time}</strong> units</td>
                <td><strong>${item.avg_waiting_time}</strong> units</td>
                <td>${item.avg_response_time} units</td>
                <td>${item.cpu_utilization}%</td>
                <td>${item.throughput}</td>
            `;
            elements.comparisonTableBody.appendChild(tr);
        });
    }

    // =========================================================================
    // 10. STEP-BY-STEP PLAYBACK ENGINE (ZERO FORCED SCROLLING)
    // =========================================================================
    function togglePlayPause() {
        if (state.isPlaying) {
            pauseSimulation();
        } else {
            startSimulation();
        }
    }

    function startSimulation() {
        if (!state.simulationData) return;
        if (state.currentTime >= state.simulationData.total_time) {
            state.currentTime = 0;
        }

        state.isPlaying = true;
        elements.playText.textContent = "Pause";
        elements.btnPlayPause.classList.add("btn-secondary");
        elements.btnPlayPause.classList.remove("btn-primary");

        state.playbackTimer = setInterval(() => {
            if (state.currentTime < state.simulationData.total_time) {
                goToTime(state.currentTime + 1);
            } else {
                pauseSimulation();
            }
        }, state.playbackSpeed);
    }

    function pauseSimulation() {
        state.isPlaying = false;
        clearInterval(state.playbackTimer);
        state.playbackTimer = null;
        elements.playText.textContent = "Play";
        elements.btnPlayPause.classList.add("btn-primary");
        elements.btnPlayPause.classList.remove("btn-secondary");
    }

    function resetPlayback() {
        pauseSimulation();
        goToTime(0);
    }

    function stepForward() {
        pauseSimulation();
        if (state.simulationData && state.currentTime < state.simulationData.total_time) {
            goToTime(state.currentTime + 1);
        }
    }

    function stepBackward() {
        pauseSimulation();
        if (state.currentTime > 0) {
            goToTime(state.currentTime - 1);
        }
    }

    function jumpToEnd() {
        pauseSimulation();
        if (state.simulationData) {
            goToTime(state.simulationData.total_time);
        }
    }

    /**
     * Updates simulation to time t.
     * ZERO scrollIntoView() or window.scrollTo() calls here.
     */
    function goToTime(t) {
        if (!state.simulationData) return;
        state.currentTime = Math.max(0, Math.min(t, state.simulationData.total_time));

        elements.currentTimeDisplay.textContent = `T = ${state.currentTime}`;
        elements.timelineScrubber.value = state.currentTime;

        const total = state.simulationData.total_time;
        const pct = total > 0 ? (state.currentTime / total) * 100 : 0;
        elements.ganttPlayhead.style.left = `${pct}%`;
        elements.playheadTag.textContent = `T=${state.currentTime}`;

        renderStepSnapshot(state.currentTime);
    }

    function handleGanttClick(e) {
        if (!state.simulationData) return;
        const rect = elements.ganttTrack.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const trackWidth = rect.width;
        if (trackWidth <= 0) return;

        const ratio = Math.max(0, Math.min(1, clickX / trackWidth));
        const clickedTime = Math.round(ratio * state.simulationData.total_time);
        pauseSimulation();
        goToTime(clickedTime);
    }

    // =========================================================================
    // 11. RENDER STEP SNAPSHOT (SIMULATION & DSA)
    // =========================================================================
    function renderStepSnapshot(t) {
        const step = state.simulationData.time_steps[t];
        if (!step) return;

        elements.eventTimeTag.textContent = t;
        elements.statusTimeBadge.textContent = t;

        // 1. CPU State Pill
        if (step.running_process) {
            const rp = step.running_process;
            elements.cpuStatusBadge.textContent = `RUNNING: ${rp.pid}`;
            elements.cpuStatusBadge.className = "core-status-pill busy";
        } else {
            elements.cpuStatusBadge.textContent = "IDLE";
            elements.cpuStatusBadge.className = "core-status-pill";
        }

        // 2. Decision Explanation Text
        if (step.decision_reason) {
            elements.eventCalloutText.textContent = step.decision_reason;
        } else if (step.events && step.events.length > 0) {
            elements.eventCalloutText.textContent = step.events.join(" | ");
        } else {
            elements.eventCalloutText.textContent = step.running_process
                ? `Process ${step.running_process.pid} is running on the CPU.`
                : "CPU is idle because no processes are ready in the queue or heap.";
        }

        // 3. Process Status Table at T
        renderLifecycleTable(step.process_statuses);

        // 4. Dynamic Data Structure Visualization
        renderDSASection(step);

        // 5. Highlight Event Log (Pure class toggle, ZERO scrolling)
        highlightEventLog(t);
    }

    function renderLifecycleTable(statuses) {
        elements.lifecycleTableBody.innerHTML = "";
        state.processes.forEach(proc => {
            const stat = statuses[proc.pid] || { status: "NOT_ARRIVED", remaining_time: proc.burst_time };
            const completed = proc.burst_time - stat.remaining_time;
            const pct = Math.min(100, Math.max(0, (completed / proc.burst_time) * 100));

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <span class="color-dot" style="background-color: ${proc.color}; margin-right: 6px;"></span>
                    <strong>${escapeHtml(proc.pid)}</strong>
                </td>
                <td>${proc.priority}</td>
                <td><span class="status-badge ${stat.status}">${stat.status.replace("_", " ")}</span></td>
                <td>${stat.remaining_time} / ${proc.burst_time} units</td>
                <td style="min-width: 100px;">
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${pct}%; background-color: ${proc.color};"></div>
                    </div>
                </td>
            `;
            elements.lifecycleTableBody.appendChild(tr);
        });
    }

    // =========================================================================
    // 12. DYNAMIC DATA STRUCTURE VISUALIZATION (QUEUE vs MIN-HEAP)
    // =========================================================================
    function renderDSASection(step) {
        const container = elements.dsaActiveContainer;
        const dsType = step.ds_type || "heap";

        if (dsType === "queue") {
            // Render FIFO Queue
            const queueItems = step.queue_snapshot || [];
            container.innerHTML = `
                <div class="dsa-header-block">
                    <span class="dsa-type-title">FIFO Queue State at T = ${step.time}</span>
                    <span class="badge-pill badge-ds">${queueItems.length} in Queue</span>
                </div>
                <div class="dsa-desc-box">
                    <strong>FIFO Queue Discipline:</strong> Processes arrive at the <code>Tail</code> and are scheduled from the <code>Head</code>.
                    For Round Robin, when a process exhausts its time slice, it is re-enqueued at the tail.
                </div>
                <div class="queue-visual-wrapper">
                    <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:var(--text-secondary);">
                        <span style="color:var(--brand-success);">&larr; HEAD (Next to run)</span>
                        <span style="color:var(--brand-primary);">TAIL (Recently enqueued) &rarr;</span>
                    </div>
                    <div class="queue-track">
                        ${queueItems.length === 0
                            ? '<span class="queue-empty-msg">FIFO Queue is currently empty.</span>'
                            : queueItems.map((item, i) => `
                                <div class="queue-cell ${item.is_head ? 'head-cell' : ''} ${item.is_tail ? 'tail-cell' : ''}">
                                    <span class="queue-pos-tag">${item.is_head ? 'HEAD [0]' : item.is_tail ? 'TAIL ['+i+']' : '['+i+']'}</span>
                                    <span class="queue-pid" style="color:${item.color};">${escapeHtml(item.pid)}</span>
                                    <span class="queue-rem">Rem: ${item.remaining_time}</span>
                                </div>
                                ${i < queueItems.length - 1 ? '<span class="queue-arrow">&larr;</span>' : ''}
                            `).join('')
                        }
                    </div>
                </div>
            `;
        } else {
            // Render Min-Heap (Binary Tree & Array Memory View)
            const heap = step.heap_snapshot || [];
            const metricName = step.heap_metric_name || "Priority / Burst";

            container.innerHTML = `
                <div class="dsa-header-block">
                    <span class="dsa-type-title">Custom Min-Heap State at T = ${step.time}</span>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <button type="button" class="btn btn-sm ${state.heapViewMode === 'tree' ? 'btn-primary' : 'btn-secondary'}" id="btnDsaTreeToggle">Binary Tree View</button>
                        <button type="button" class="btn btn-sm ${state.heapViewMode === 'array' ? 'btn-primary' : 'btn-secondary'}" id="btnDsaArrayToggle">Array Memory View</button>
                        <span class="badge-pill badge-ds">${heap.length} in Heap</span>
                    </div>
                </div>
                <div class="dsa-desc-box">
                    <strong>Binary Min-Heap (Key: ${escapeHtml(metricName)}):</strong>
                    Root node holds the process with the minimum sort key. Insertion and extraction take <code>O(log N)</code>.
                    Parent at <code>(i - 1) // 2</code> &bull; Left child at <code>2i + 1</code> &bull; Right child at <code>2i + 2</code>.
                </div>

                <div class="heap-tree-wrap ${state.heapViewMode === 'tree' ? '' : 'hidden'}" id="dsaTreeWrapper">
                    <svg class="heap-tree-svg" id="dsaSvg" viewBox="0 0 500 240" preserveAspectRatio="xMidYMid meet"></svg>
                    <div class="heap-empty-message ${heap.length === 0 ? '' : 'hidden'}">Ready Min-Heap is currently empty.</div>
                </div>

                <div class="heap-array-wrap ${state.heapViewMode === 'array' ? '' : 'hidden'}" id="dsaArrayWrapper">
                    <div class="heap-cells-grid">
                        ${heap.length === 0
                            ? '<span class="text-muted" style="font-style:italic; font-size:13px;">Heap array is empty.</span>'
                            : heap.map(node => `
                                <div class="array-node-cell ${node.index === 0 ? 'root-node' : ''}">
                                    <span class="node-idx">[${node.index}]</span>
                                    <span class="node-pid" style="color:${node.color};">${escapeHtml(node.pid)}</span>
                                    <span class="node-key">${escapeHtml(metricName)}: ${node.sort_key_display}</span>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            `;

            // Draw SVG Tree
            drawHeapTreeSvg(heap, document.getElementById("dsaSvg"));

            // Sub-toggles listeners
            document.getElementById("btnDsaTreeToggle").addEventListener("click", () => {
                state.heapViewMode = "tree";
                renderDSASection(step);
            });
            document.getElementById("btnDsaArrayToggle").addEventListener("click", () => {
                state.heapViewMode = "array";
                renderDSASection(step);
            });
        }
    }

    function drawHeapTreeSvg(heap, svg) {
        if (!svg || heap.length === 0) return;
        svg.innerHTML = "";

        const coords = [
            { x: 250, y: 38 },   // 0 (root)
            { x: 140, y: 95 },   // 1
            { x: 360, y: 95 },   // 2
            { x: 80,  y: 155 },  // 3
            { x: 190, y: 155 },  // 4
            { x: 310, y: 155 },  // 5
            { x: 420, y: 155 },  // 6
            { x: 50,  y: 205 },  // 7
            { x: 110, y: 205 },  // 8
            { x: 160, y: 205 },  // 9
            { x: 220, y: 205 },  // 10
            { x: 280, y: 205 },  // 11
            { x: 340, y: 205 },  // 12
            { x: 390, y: 205 },  // 13
            { x: 450, y: 205 }   // 14
        ];

        // Draw edges
        heap.forEach(node => {
            const idx = node.index;
            if (idx >= coords.length) return;
            const p = coords[idx];

            if (node.left_child_index !== null && node.left_child_index < heap.length && node.left_child_index < coords.length) {
                const l = coords[node.left_child_index];
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", p.x); line.setAttribute("y1", p.y);
                line.setAttribute("x2", l.x); line.setAttribute("y2", l.y);
                line.setAttribute("stroke", "#475569"); line.setAttribute("stroke-width", "2");
                svg.appendChild(line);
            }

            if (node.right_child_index !== null && node.right_child_index < heap.length && node.right_child_index < coords.length) {
                const r = coords[node.right_child_index];
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", p.x); line.setAttribute("y1", p.y);
                line.setAttribute("x2", r.x); line.setAttribute("y2", r.y);
                line.setAttribute("stroke", "#475569"); line.setAttribute("stroke-width", "2");
                svg.appendChild(line);
            }
        });

        // Draw nodes
        heap.forEach(node => {
            const idx = node.index;
            if (idx >= coords.length) return;
            const c = coords[idx];
            const isRoot = idx === 0;

            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

            if (isRoot) {
                const ring = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                ring.setAttribute("cx", c.x); ring.setAttribute("cy", c.y);
                ring.setAttribute("r", "24"); ring.setAttribute("fill", "none");
                ring.setAttribute("stroke", "#f59e0b"); ring.setAttribute("stroke-width", "2");
                g.appendChild(ring);
            }

            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", c.x); circle.setAttribute("cy", c.y);
            circle.setAttribute("r", "19"); circle.setAttribute("fill", node.color || "#3b82f6");
            circle.setAttribute("stroke", "#ffffff"); circle.setAttribute("stroke-width", "1.5");
            g.appendChild(circle);

            const textPid = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textPid.setAttribute("x", c.x); textPid.setAttribute("y", c.y - 1);
            textPid.setAttribute("text-anchor", "middle"); textPid.setAttribute("dominant-baseline", "central");
            textPid.setAttribute("fill", "#ffffff"); textPid.setAttribute("font-family", "Outfit, sans-serif");
            textPid.setAttribute("font-weight", "700"); textPid.setAttribute("font-size", "11.5");
            textPid.textContent = node.pid;
            g.appendChild(textPid);

            const textKey = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textKey.setAttribute("x", c.x); textKey.setAttribute("y", c.y + 11);
            textKey.setAttribute("text-anchor", "middle"); textKey.setAttribute("dominant-baseline", "central");
            textKey.setAttribute("fill", "#ffffff"); textKey.setAttribute("font-family", "JetBrains Mono, monospace");
            textKey.setAttribute("font-size", "8"); textKey.setAttribute("font-weight", "600");
            textKey.textContent = node.sort_key_display;
            g.appendChild(textKey);

            const textIdx = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textIdx.setAttribute("x", c.x + 15); textIdx.setAttribute("y", c.y - 15);
            textIdx.setAttribute("text-anchor", "middle"); textIdx.setAttribute("fill", "#94a3b8");
            textIdx.setAttribute("font-family", "JetBrains Mono, monospace"); textIdx.setAttribute("font-size", "9");
            textIdx.textContent = `[${idx}]`;
            g.appendChild(textIdx);

            svg.appendChild(g);
        });
    }

    // =========================================================================
    // 13. GANTT CHART RENDERING
    // =========================================================================
    function renderGanttChart(blocks, totalTime) {
        elements.ganttTrack.innerHTML = "";
        elements.ganttAxis.innerHTML = "";
        elements.ganttLegend.innerHTML = "";

        if (!blocks || blocks.length === 0 || totalTime === 0) {
            elements.ganttTrack.innerHTML = "<div style='display:flex;align-items:center;justify-content:center;width:100%;color:#94a3b8;font-size:13px;'>No simulation data.</div>";
            return;
        }

        const seenPids = new Set();
        blocks.forEach(b => {
            if (!seenPids.has(b.pid)) {
                seenPids.add(b.pid);
                const chip = document.createElement("div");
                chip.className = "legend-chip";
                chip.innerHTML = `
                    <span class="color-dot" style="background-color: ${b.color};"></span>
                    <span>${b.pid === 'IDLE' ? 'Idle' : escapeHtml(b.pid)}</span>
                `;
                elements.ganttLegend.appendChild(chip);
            }
        });

        blocks.forEach(b => {
            const duration = b.end - b.start;
            const widthPct = (duration / totalTime) * 100;

            const div = document.createElement("div");
            div.className = `gantt-block ${b.pid === 'IDLE' ? 'idle-block' : ''}`;
            div.style.width = `${widthPct}%`;
            if (b.pid !== "IDLE") {
                div.style.backgroundColor = b.color;
            }
            div.setAttribute("title", `${b.pid}: T=${b.start} → T=${b.end} (${duration} units)`);

            div.innerHTML = `
                <span class="gantt-block-pid">${b.pid}</span>
                <span class="gantt-block-time">${b.start}&ndash;${b.end}</span>
            `;
            elements.ganttTrack.appendChild(div);
        });

        const timePoints = new Set([0, totalTime]);
        blocks.forEach(b => {
            timePoints.add(b.start);
            timePoints.add(b.end);
        });

        const sortedPoints = Array.from(timePoints).sort((a, b) => a - b);
        sortedPoints.forEach(pt => {
            const tick = document.createElement("div");
            tick.className = "gantt-tick";
            tick.style.left = `${(pt / totalTime) * 100}%`;
            tick.textContent = pt;
            elements.ganttAxis.appendChild(tick);
        });
    }

    // =========================================================================
    // 14. PERFORMANCE METRICS
    // =========================================================================
    function renderMetrics(data) {
        const sum = data.summary_metrics;
        elements.kpiTat.textContent = sum.avg_turnaround_time;
        elements.kpiWt.textContent = sum.avg_waiting_time;
        elements.kpiRt.textContent = sum.avg_response_time;
        elements.kpiCpuUtil.textContent = `${sum.cpu_utilization}%`;
        elements.kpiThroughput.textContent = `${sum.throughput} / unit`;

        elements.metricsTableBody.innerHTML = "";
        data.process_metrics.forEach(pm => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <span class="color-dot" style="background-color: ${pm.color}; margin-right: 6px;"></span>
                    <strong>${escapeHtml(pm.pid)}</strong>
                </td>
                <td>${pm.arrival_time}</td>
                <td>${pm.burst_time}</td>
                <td>${pm.priority}</td>
                <td>${pm.start_time !== null ? pm.start_time : '-'}</td>
                <td><strong>${pm.completion_time !== null ? pm.completion_time : '-'}</strong></td>
                <td><strong>${pm.turnaround_time !== null ? pm.turnaround_time : '-'}</strong></td>
                <td><strong>${pm.waiting_time !== null ? pm.waiting_time : '-'}</strong></td>
                <td><strong>${pm.response_time !== null ? pm.response_time : '-'}</strong></td>
            `;
            elements.metricsTableBody.appendChild(tr);
        });
    }

    // =========================================================================
    // 15. EVENT LOG (NO AUTO SCROLLING)
    // =========================================================================
    function renderFullEventLog(eventsLog) {
        elements.eventsLogContainer.innerHTML = "";
        elements.logCountBadge.textContent = `${eventsLog.length} events recorded`;

        if (!eventsLog || eventsLog.length === 0) {
            elements.eventsLogContainer.innerHTML = "<div class='log-row'><span class='log-text'>No events recorded yet.</span></div>";
            return;
        }

        eventsLog.forEach(ev => {
            const row = document.createElement("div");
            row.className = `log-row ${ev.type || ''}`;
            row.setAttribute("data-time", ev.time);
            row.innerHTML = `
                <span class="log-time-tag">[T=${ev.time}]</span>
                <span class="log-type-tag">${ev.type || 'INFO'}</span>
                <span class="log-text">${escapeHtml(ev.message)}</span>
            `;
            elements.eventsLogContainer.appendChild(row);
        });
    }

    function highlightEventLog(time) {
        const rows = elements.eventsLogContainer.querySelectorAll(".log-row");
        rows.forEach(row => {
            const rowTime = parseInt(row.getAttribute("data-time"), 10);
            if (rowTime === time) {
                row.classList.add("active-tick");
            } else {
                row.classList.remove("active-tick");
            }
        });
    }

    // =========================================================================
    // 16. UTILITIES
    // =========================================================================
    function showError(msg) {
        elements.errorMessageText.textContent = msg;
        elements.errorBanner.classList.remove("hidden");
    }

    function hideError() {
        elements.errorBanner.classList.add("hidden");
    }

    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    init();
});
