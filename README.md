# CPU Scheduling Lab ⚡

An educational Data Structures and Algorithms (DSA) learning platform that simulates and visualizes **CPU Scheduling Algorithms** using their actual underlying data structures implemented manually from scratch in Python.

Developed as a college computer science DSA/OS project to demonstrate how operating system kernel schedulers organize ready queues, make process dispatching decisions, handle preemptions, and calculate core performance metrics.

---

## 📌 Supported Scheduling Algorithms

The platform categorizes and implements all six standard operating system scheduling algorithms:

### A. Preemptive Algorithms
1. **Round Robin (RR)**
   * **Data Structure**: `FIFOQueue` (First-In, First-Out Queue)
   * **Process Selection Rule**: Dispatches the process at the head of the FIFO ready queue.
   * **Official Description**: *"Gives each ready process a fixed time slice called a time quantum. Unfinished processes return to the end of the FIFO ready queue."*
   * **Preemption**: Occurs when execution time reaches the configured Time Quantum ($Q$).

2. **Shortest Remaining Time First (SRTF)**
   * **Data Structure**: `MinHeap` (Key: Remaining Execution Time)
   * **Process Selection Rule**: Continuously selects the ready process with the shortest remaining execution time from the Min-Heap.
   * **Official Description**: *"Selects the ready process with the shortest remaining execution time. A running process can be interrupted when another process has a shorter remaining time."*
   * **Preemption**: Occurs whenever an arriving process has strictly shorter remaining burst time than the currently executing process.

3. **Preemptive Priority Scheduling**
   * **Data Structure**: `MinHeap` (Key: Numerical Priority)
   * **Process Selection Rule**: Selects the ready process with the highest priority (smallest numerical value) from the Min-Heap.
   * **Official Description**: *"Selects the highest-priority ready process. A running process can be interrupted when a higher-priority process arrives."*
   * **Preemption**: Occurs whenever an arriving process has strictly higher priority (smaller numerical value) than the currently executing process.

### B. Non-Preemptive Algorithms
1. **First-Come, First-Served (FCFS)**
   * **Data Structure**: `FIFOQueue`
   * **Process Selection Rule**: Executes processes strictly in the order they arrive in the ready queue.
   * **Official Description**: *"Executes processes in arrival order. Once a process starts, it runs until completion."*
   * **Behavior**: Non-preemptive. Demonstrates the Convoy Effect.

2. **Shortest Job First (SJF)**
   * **Data Structure**: `MinHeap` (Key: Initial Burst Time)
   * **Process Selection Rule**: When the CPU becomes free, selects the ready process with the smallest initial burst time from the Min-Heap.
   * **Official Description**: *"Selects the ready process with the shortest original burst time. The selected process runs until completion."*
   * **Behavior**: Non-preemptive. Once started, a process runs until completion. Proven to provide the minimal average waiting time among all non-preemptive algorithms.

3. **Non-Preemptive Priority Scheduling**
   * **Data Structure**: `MinHeap` (Key: Numerical Priority)
   * **Process Selection Rule**: When the CPU is free, selects the ready process with the highest priority (smallest numerical value) from the Min-Heap.
   * **Official Description**: *"Selects the highest-priority ready process. Once started, that process runs until completion."*
   * **Behavior**: Non-preemptive. The selected process executes until completion without interruption.

---

## 🧠 Data Structures Implemented from Scratch

### 1. Custom Binary Min-Heap (`scheduler/data_structures.py`)
Implemented manually using Python arrays without importing `heapq`:
* **Heap Mapping**:
  * Parent at index `(i - 1) // 2`
  * Left child at index `2i + 1`
  * Right child at index `2i + 2`
* **Heap Invariant**: Parent key $\le$ child keys at all times. Maintained via `_heapify_up()` on insertion and `_heapify_down()` on extraction.
* **Operations**:
  * `push()`: Appends element and sifts up ($\mathcal{O}(\log N)$).
  * `pop()`: Extracts root, places last element at root, and sifts down ($\mathcal{O}(\log N)$).
  * `peek()`: Returns root element without extraction ($\mathcal{O}(1)$).
* **Snapshots**: Generates structured snapshots containing parent and child pointer indices for dual visualization:
  * **SVG Binary Tree View**
  * **Zero-Indexed Array Memory View**

### 2. Custom FIFO Queue (`scheduler/data_structures.py`)
Implemented manually without importing `queue.Queue`:
* **Operations**:
  * `enqueue()`: Appends a process to the tail ($\mathcal{O}(1)$).
  * `dequeue()`: Extracts and returns the process from the head ($\mathcal{O}(N)$ or pointer-based).
  * `peek()`: Returns the head element ($\mathcal{O}(1)$).
* **Snapshots**: Generates head-to-tail queue state snapshots showing Head, Tail, and position indices.

---

## ⚖️ Deterministic Tie-Breaking Rules

All algorithms and data structures implement a unified, three-tiered deterministic tie-breaking policy:
1. **Primary Metric**:
   * Priority Scheduling: Numerical priority (smaller is higher).
   * SJF: Initial burst time.
   * SRTF: Remaining burst time.
   * FCFS & Round Robin: Arrival order.
2. **Secondary Metric**: Earlier arrival time ($AT$).
3. **Tertiary Metric**: Natural numeric Process ID (`pid_sort_key`):
   * Parses alphanumeric prefixes and integers so that numeric order is preserved.
   * Ensures that `P2` strictly precedes `P10` (unlike standard alphabetical comparison where `"P10" < "P2"`).

---

## ⏱️ Round Robin Event Ordering at Quantum Expiration

When a process's time quantum expires at tick $T$ simultaneously with new process arrivals:
1. **New arrivals at $T$** are enqueued into the FIFO ready queue tail first (sorted by `pid_sort_key`).
2. **The expiring process** is preempted and re-enqueued at the tail *behind* the newly arrived processes.
3. **Dispatch**: The process at the head of the ready queue is dispatched.
4. **Completion**: If a process finishes its burst at tick $T$, metrics are finalized immediately without appending a spurious idle block.

---

## 📐 Formulas & Performance Metrics

* **Completion Time ($CT$)**: Time tick at which the process finishes execution.
* **Turnaround Time ($TAT$)**:
  $$\text{TAT} = CT - \text{Arrival Time } (AT)$$
* **Waiting Time ($WT$)**:
  $$\text{WT} = \text{TAT} - \text{Original Burst Time } (BT)$$
* **Response Time ($RT$)**:
  $$\text{RT} = \text{First CPU Start Time } (ST) - \text{Arrival Time } (AT)$$
* **CPU Utilization (%)**:
  $$\text{CPU Utilization} = \frac{\sum BT}{\text{Total Makespan}} \times 100\%$$
  *(Idle time is strictly excluded from busy time).*
* **Throughput**:
  $$\text{Throughput} = \frac{N_{\text{completed processes}}}{\text{Total Makespan}}$$
* **Zero Elapsed Time**: When makespan is 0, CPU utilization and throughput are safely defined as `0.0`.

---

## 🛡️ Input Validation & Limits

Strict validation is performed on both frontend and backend (Flask HTTP 400):
* **Process Count**: $1 \le N \le 50$.
* **Process ID**: Non-empty, unique, maximum length 20 characters.
* **Arrival Time**: Integer $0 \le AT \le 5000$. Booleans and decimals are rejected.
* **Burst Time**: Integer $1 \le BT \le 500$. Booleans and decimals are rejected.
* **Priority**: Integer $-1000 \le Priority \le 1000$. Smaller numbers indicate higher priority.
* **Time Quantum**: Integer $1 \le Q \le 100$. Booleans and decimals are rejected.
* **Malformed JSON**: Returns HTTP 400 with a clean error message.

---

## ⚙️ Assumptions

1. Single CPU core architecture.
2. Context switch overhead is assumed to be 0 for standard academic analysis.
3. Preemption only occurs when an arriving process has *strictly* shorter remaining time or *strictly* higher priority. If equal, the running process continues to avoid unnecessary context switching.

---

## 📸 Project Screenshots

### 1. Process Setup & Algorithm Selection

Configure processes and select a CPU scheduling algorithm.

<p align="center">
  <img src="screenshots/1. Process Setup & Algorithm Selection.png" alt="Process Setup and Algorithm Selection" width="900">
</p>

### 2. Simulation & Gantt Chart

View process execution and follow the scheduling timeline.

<p align="center">
  <img src="screenshots/2. Simulation & Gantt Chart.png" alt="Simulation and Gantt Chart" width="900">
</p>

### 3. Data Structure Visualization

Visualize the data structures used by the selected scheduling algorithm.

<p align="center">
  <img src="screenshots/3. Data Structure Visualization.png" alt="Data Structure Visualization" width="900">
</p>

### 4. Performance Analysis & Comparison

Analyze scheduling metrics and compare algorithm performance.

<p align="center">
  <img src="screenshots/4. Performance Analysis & Comparison.png" alt="Performance Analysis and Comparison" width="900">
</p>

### 5. Algorithm Reference & Theory

Learn about the scheduling algorithms and their working methods.

<p align="center">
  <img src="screenshots/5. Algorithm Reference & Theory.png" alt="Algorithm Reference and Theory" width="900">
</p>

### 6. About Project

View project information, technologies, and development details.

<p align="center">
  <img src="screenshots/6. About Project.png" alt="About Project" width="900">
</p>

### 7. Algorithm Performance Comparison

Compare the performance of different CPU scheduling algorithms.

<p align="center">
  <img src="screenshots/Algorithm Performance Comparison.png" alt="Algorithm Performance Comparison" width="900">
</p>

### 8. Gantt Chart

View the CPU execution order and process scheduling intervals.

<p align="center">
  <img src="screenshots/gantt chart.png" alt="CPU Scheduling Gantt Chart" width="900">
</p>

---

## 📁 Project Structure

```
CPU-Scheduling-Lab/
├── app.py                    # Flask server with /api/simulate, /api/compare, and /api/presets
├── requirements.txt           # Python dependencies (Flask)
├── README.md                  # Comprehensive project documentation
├── scheduler/                # Core Python DSA package
│   ├── __init__.py           # Package exports
│   ├── process.py            # Process lifecycle model & natural PID sorting
│   ├── data_structures.py    # Manual MinHeap & FIFOQueue implementations
│   └── algorithms.py         # All 6 scheduling algorithms & comparison runner
├── templates/
│   └── index.html            # Semantic layout: Header, Nav, 6 Sections, Footer
├── static/
│   ├── style.css             # Responsive, academic CSS (Dark & Light themes)
│   └── script.js             # Playback engine, Queue & Heap SVG visualizers, zero auto-scrolling
└── tests/
    ├── __init__.py
    └── test_scheduler.py     # Unit tests verifying all algorithms, data structures, and APIs
```

---

## 🚀 Running the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python3 app.py
```
Open your browser at:
```
http://127.0.0.1:5001/
```

### 3. Run Automated Unit Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
