"""
scheduler/algorithms.py
Implements comprehensive CPU Scheduling Algorithms using their actual Data Structures:

PREEMPTIVE:
1. Round Robin (RR) -> Uses FIFOQueue
2. Shortest Remaining Time First (SRTF) -> Uses MinHeap (key: remaining_time)
3. Preemptive Priority Scheduling -> Uses MinHeap (key: priority)

NON-PREEMPTIVE:
1. First-Come, First-Served (FCFS) -> Uses FIFOQueue
2. Shortest Job First (SJF) -> Uses MinHeap (key: burst_time)
3. Non-Preemptive Priority Scheduling -> Uses MinHeap (key: priority)
"""

from typing import List, Dict, Any, Optional, Tuple
from scheduler.process import Process, pid_sort_key
from scheduler.data_structures import MinHeap, FIFOQueue


def validate_processes(
    raw_processes: List[Dict[str, Any]],
    quantum: Optional[int] = None
) -> Tuple[bool, Optional[str], List[Process], int]:
    """
    Validates process input and time quantum with strict limits.
    Enforces:
    - Non-empty list, max 50 processes
    - Unique, non-empty Process IDs (max 20 chars)
    - Integer Arrival Time (0 <= AT <= 5000), no booleans or decimals
    - Integer Burst Time (1 <= BT <= 500), no booleans or decimals
    - Integer Priority (-1000 <= Priority <= 1000), no booleans or decimals
    - Valid integer Time Quantum (1 <= Q <= 100), no booleans or decimals
    """
    if not isinstance(raw_processes, list):
        return False, "Process data must be a valid JSON array.", [], 2

    if len(raw_processes) == 0:
        return False, "At least one process is required.", [], 2

    if len(raw_processes) > 50:
        return False, "Maximum limit of 50 processes exceeded.", [], 2

    pids_seen = set()
    validated_processes = []
    default_colors = [
        "#3b82f6", "#ec4899", "#10b981", "#f59e0b",
        "#06b6d4", "#8b5cf6", "#f43f5e", "#14b8a6", "#6366f1"
    ]

    for idx, p_data in enumerate(raw_processes):
        if not isinstance(p_data, dict):
            return False, f"Process #{idx + 1} must be a valid JSON object.", [], 2

        raw_pid = p_data.get("pid")
        if raw_pid is None or str(raw_pid).strip() == "":
            return False, f"Process #{idx + 1} has an empty Process ID.", [], 2

        pid = str(raw_pid).strip().upper()
        if len(pid) > 20:
            return False, f"Process #{idx + 1} ID '{pid}' is too long (maximum 20 characters).", [], 2

        if pid in pids_seen:
            return False, f"Duplicate Process ID '{pid}'. Process IDs must be unique.", [], 2
        pids_seen.add(pid)

        # Arrival Time Validation
        raw_at = p_data.get("arrival_time")
        if raw_at is None or isinstance(raw_at, bool):
            return False, f"Process {pid}: Arrival Time cannot be null or boolean.", [], 2
        if isinstance(raw_at, float) and not raw_at.is_integer():
            return False, f"Process {pid}: Arrival Time must be an integer, not a decimal.", [], 2
        try:
            arrival_time = int(raw_at)
            if arrival_time < 0:
                return False, f"Process {pid}: Arrival Time must be >= 0.", [], 2
            if arrival_time > 5000:
                return False, f"Process {pid}: Arrival Time exceeds maximum limit of 5000.", [], 2
        except (ValueError, TypeError):
            return False, f"Process {pid}: Arrival Time must be a valid integer.", [], 2

        # Burst Time Validation
        raw_bt = p_data.get("burst_time")
        if raw_bt is None or isinstance(raw_bt, bool):
            return False, f"Process {pid}: Burst Time cannot be null or boolean.", [], 2
        if isinstance(raw_bt, float) and not raw_bt.is_integer():
            return False, f"Process {pid}: Burst Time must be an integer, not a decimal.", [], 2
        try:
            burst_time = int(raw_bt)
            if burst_time < 1:
                return False, f"Process {pid}: Burst Time must be at least 1.", [], 2
            if burst_time > 500:
                return False, f"Process {pid}: Burst Time exceeds maximum limit of 500.", [], 2
        except (ValueError, TypeError):
            return False, f"Process {pid}: Burst Time must be a valid integer >= 1.", [], 2

        # Priority Validation
        raw_prio = p_data.get("priority", 1)
        if raw_prio is None or isinstance(raw_prio, bool):
            return False, f"Process {pid}: Priority cannot be null or boolean.", [], 2
        if isinstance(raw_prio, float) and not raw_prio.is_integer():
            return False, f"Process {pid}: Priority must be an integer, not a decimal.", [], 2
        try:
            priority = int(raw_prio)
            if priority < -1000 or priority > 1000:
                return False, f"Process {pid}: Priority must be between -1000 and 1000.", [], 2
        except (ValueError, TypeError):
            return False, f"Process {pid}: Priority must be a valid integer.", [], 2

        color = p_data.get("color")
        if not color or not str(color).startswith("#"):
            color = default_colors[idx % len(default_colors)]

        validated_processes.append(
            Process(pid=pid, arrival_time=arrival_time, burst_time=burst_time, priority=priority, color=color)
        )

    validated_quantum = 2
    if quantum is not None:
        if isinstance(quantum, bool):
            return False, "Time Quantum cannot be a boolean.", [], 2
        if isinstance(quantum, float) and not quantum.is_integer():
            return False, "Time Quantum must be an integer, not a decimal.", [], 2
        try:
            q_val = int(quantum)
            if q_val < 1:
                return False, "Time Quantum for Round Robin must be at least 1.", [], 2
            if q_val > 100:
                return False, "Time Quantum cannot exceed 100.", [], 2
            validated_quantum = q_val
        except (ValueError, TypeError):
            return False, "Time Quantum must be a valid positive integer.", [], 2

    return True, None, validated_processes, validated_quantum


def _merge_gantt_blocks(raw_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merges consecutive 1-unit Gantt blocks for the same PID into contiguous blocks."""
    if not raw_blocks:
        return []

    merged = []
    current = dict(raw_blocks[0])

    for b in raw_blocks[1:]:
        if b["pid"] == current["pid"] and b["start"] == current["end"]:
            current["end"] = b["end"]
        else:
            merged.append(current)
            current = dict(b)
    merged.append(current)
    return merged


def _calculate_metrics(completed_processes: List[Process], total_makespan: int) -> Dict[str, Any]:
    n = len(completed_processes)
    if n == 0 or total_makespan == 0:
        return {
            "avg_turnaround_time": 0.0,
            "avg_waiting_time": 0.0,
            "avg_response_time": 0.0,
            "cpu_utilization": 0.0,
            "throughput": 0.0,
            "total_time": total_makespan,
            "total_burst_time": 0,
            "idle_time": total_makespan
        }

    total_tat = sum(p.turnaround_time or 0 for p in completed_processes)
    total_wt = sum(p.waiting_time or 0 for p in completed_processes)
    total_rt = sum(p.response_time or 0 for p in completed_processes)
    total_bt = sum(p.burst_time for p in completed_processes)

    cpu_util = round((total_bt / total_makespan) * 100, 2) if total_makespan > 0 else 0.0
    throughput = round(n / total_makespan, 4) if total_makespan > 0 else 0.0

    return {
        "avg_turnaround_time": round(total_tat / n, 2),
        "avg_waiting_time": round(total_wt / n, 2),
        "avg_response_time": round(total_rt / n, 2),
        "cpu_utilization": min(cpu_util, 100.0),
        "throughput": throughput,
        "total_time": total_makespan,
        "total_burst_time": total_bt,
        "idle_time": max(0, total_makespan - total_bt)
    }


def _build_complete_dsa_snapshot(
    algo_key: str,
    processes: List[Process],
    total_pushes: int,
    total_pops: int,
    peak_size: int,
    dispatch_order: List[str]
) -> Dict[str, Any]:
    """Generates the full canonical data structure snapshot and lifecycle stats."""
    algo_key = algo_key.lower().strip()
    if algo_key in ("round_robin", "rr", "fcfs"):
        full_q = FIFOQueue()
        for p in sorted(processes, key=lambda x: (x.arrival_time, pid_sort_key(x.pid))):
            full_q.enqueue(p.clone())
        metric = "Arrival Order (Time-Sliced)" if "round_robin" in algo_key or algo_key == "rr" else "Arrival Time (Strict FIFO)"
        return {
            "ds_type": "queue",
            "ds_name": "FIFO Ready Queue",
            "metric_name": metric,
            "complexity": "O(1) Enqueue & Dequeue",
            "total_pushes": total_pushes,
            "total_pops": total_pops,
            "peak_size": peak_size,
            "dispatch_order": dispatch_order,
            "complete_snapshot": full_q.get_snapshot()
        }
    else:
        if algo_key == "srtf":
            key_func = lambda p: (p.remaining_time, p.arrival_time, pid_sort_key(p.pid))
            metric = "Remaining Execution Time"
        elif algo_key == "sjf":
            key_func = lambda p: (p.burst_time, p.arrival_time, pid_sort_key(p.pid))
            metric = "Initial Burst Time"
        else:
            key_func = lambda p: (p.priority, p.arrival_time, pid_sort_key(p.pid))
            metric = "Priority (Lowest Value = Highest Priority)"

        full_heap = MinHeap(key_func=key_func)
        for p in processes:
            full_heap.push(p.clone())

        return {
            "ds_type": "heap",
            "ds_name": "Binary Min-Heap",
            "metric_name": metric,
            "complexity": "O(log N) Insert & Extract-Min",
            "total_pushes": total_pushes,
            "total_pops": total_pops,
            "peak_size": peak_size,
            "dispatch_order": dispatch_order,
            "complete_snapshot": full_heap.get_snapshot()
        }


# ==============================================================================
# 1. ROUND ROBIN (PREEMPTIVE, FIFO QUEUE)
# ==============================================================================
def schedule_round_robin(processes: List[Process], quantum: int = 2) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    queue = FIFOQueue()
    total_processes = len(procs)
    completed_processes: List[Process] = []

    total_pushes = 0
    total_pops = 0
    peak_size = 0
    dispatch_order: List[str] = []

    current_time = 0
    running_process: Optional[Process] = None
    quantum_elapsed = 0

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        # 1. New process arrivals at current_time enter FIFO Queue (sorted deterministically)
        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                queue.enqueue(arr_proc)
                total_pushes += 1
                peak_size = max(peak_size, queue.size())
                msg = f"Process {arr_proc.pid} arrived -> Enqueued to Ready Queue tail."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        # 2. Check if running process expired its time quantum
        if running_process is not None and quantum_elapsed >= quantum:
            # Quantum expired -> Re-enqueue to queue tail behind any newly arrived processes
            re_msg = f"Time Quantum of {quantum} units expired for {running_process.pid}. Re-enqueued to Queue tail."
            tick_events.append(re_msg)
            events_log.append({"time": current_time, "type": "PREEMPT", "pid": running_process.pid, "message": re_msg})
            queue.enqueue(running_process)
            total_pushes += 1
            peak_size = max(peak_size, queue.size())
            running_process = None
            quantum_elapsed = 0

        # 3. If CPU is idle, dispatch next process from FIFO Queue head
        if running_process is None:
            if not queue.is_empty():
                running_process = queue.dequeue()
                total_pops += 1
                dispatch_order.append(running_process.pid)
                quantum_elapsed = 0
                if running_process.start_time is None:
                    running_process.start_time = current_time
                disp_msg = f"CPU dispatched {running_process.pid} from Queue head (Remaining Burst: {running_process.remaining_time})."
                tick_events.append(disp_msg)
                events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": disp_msg})

        # Formulate explanation for this tick
        if running_process is not None:
            decision_reason = (f"Round Robin: {running_process.pid} is running "
                               f"(Slice: {quantum_elapsed + 1}/{quantum}, Remaining: {running_process.remaining_time}).")
        else:
            decision_reason = "CPU is idle (Ready FIFO Queue is empty)."

        # Record statuses
        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        # Snapshot
        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "queue",
            "queue_snapshot": queue.get_snapshot(),
            "heap_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        # 4. Execute 1 time unit
        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)
            quantum_elapsed += 1
            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                comp_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": comp_msg})
                running_process = None
                quantum_elapsed = 0
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    # Check last process completion if any
    if running_process is not None and running_process.remaining_time <= 0:
        running_process.finalize_metrics(current_time)
        completed_processes.append(running_process)

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "queue",
        "queue_snapshot": [],
        "heap_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, p.pid))
    return {
        "algorithm": "Round Robin (RR)",
        "algorithm_key": "round_robin",
        "category": "Preemptive",
        "data_structure": "FIFO Queue",
        "quantum": quantum,
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time),
        "dsa_summary": _build_complete_dsa_snapshot("round_robin", processes, total_pushes, total_pops, peak_size, dispatch_order)
    }


# ==============================================================================
# 2. SHORTEST REMAINING TIME FIRST (PREEMPTIVE, MIN-HEAP KEYED BY REMAINING TIME)
# ==============================================================================
def schedule_srtf(processes: List[Process]) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    # Min-Heap sorting by remaining_time, tie-breaker: arrival_time, then pid_sort_key
    heap = MinHeap(key_func=lambda p: (p.remaining_time, p.arrival_time, pid_sort_key(p.pid)))
    total_processes = len(procs)
    completed_processes: List[Process] = []

    total_pushes = 0
    total_pops = 0
    peak_size = 0
    dispatch_order: List[str] = []

    current_time = 0
    running_process: Optional[Process] = None

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        # 1. Process arrivals (sorted deterministically)
        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                heap.push(arr_proc)
                total_pushes += 1
                peak_size = max(peak_size, heap.size())
                msg = f"Process {arr_proc.pid} arrived (Remaining: {arr_proc.remaining_time}) -> Pushed into SRTF Min-Heap."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        # 2. Check for preemption or dispatch
        if running_process is not None:
            if not heap.is_empty() and heap.peek().remaining_time < running_process.remaining_time:
                preempted = running_process
                heap.push(preempted)
                total_pushes += 1
                peak_size = max(peak_size, heap.size())
                running_process = heap.pop()
                total_pops += 1
                dispatch_order.append(running_process.pid)
                p_msg = (f"PREEMPTION at T={current_time}: {running_process.pid} (Remaining: {running_process.remaining_time}) "
                         f"interrupted {preempted.pid} (Remaining: {preempted.remaining_time}).")
                tick_events.append(p_msg)
                events_log.append({"time": current_time, "type": "PREEMPT", "pid": running_process.pid, "message": p_msg})
                if running_process.start_time is None:
                    running_process.start_time = current_time
        else:
            if not heap.is_empty():
                running_process = heap.pop()
                total_pops += 1
                dispatch_order.append(running_process.pid)
                if running_process.start_time is None:
                    running_process.start_time = current_time
                d_msg = f"CPU dispatched {running_process.pid} with shortest remaining time ({running_process.remaining_time})."
                tick_events.append(d_msg)
                events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": d_msg})

        # Decision reason
        if running_process is not None:
            decision_reason = f"SRTF: {running_process.pid} is running (Shortest Remaining Time: {running_process.remaining_time} units)."
        else:
            decision_reason = "CPU is idle (No ready processes in Min-Heap)."

        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "heap",
            "heap_metric_name": "Remaining Time",
            "heap_snapshot": heap.get_snapshot(),
            "queue_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        # 3. Execute 1 time unit
        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)

            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                c_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": c_msg})
                running_process = None
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "heap",
        "heap_metric_name": "Remaining Time",
        "heap_snapshot": [],
        "queue_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, p.pid))
    return {
        "algorithm": "Shortest Remaining Time First (SRTF)",
        "algorithm_key": "srtf",
        "category": "Preemptive",
        "data_structure": "Min-Heap (key: Remaining Time)",
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time)
    }


# ==============================================================================
# 3. PREEMPTIVE PRIORITY SCHEDULING (MIN-HEAP KEYED BY PRIORITY)
# ==============================================================================
def schedule_priority_preemptive(processes: List[Process]) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    heap = MinHeap(key_func=lambda p: (p.priority, p.arrival_time, pid_sort_key(p.pid)))
    total_processes = len(procs)
    completed_processes: List[Process] = []

    current_time = 0
    running_process: Optional[Process] = None

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                heap.push(arr_proc)
                msg = f"Process {arr_proc.pid} arrived (Priority: {arr_proc.priority}) -> Pushed into Priority Min-Heap."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        if running_process is not None:
            if not heap.is_empty() and heap.peek().priority < running_process.priority:
                preempted = running_process
                heap.push(preempted)
                running_process = heap.pop()
                p_msg = (f"PREEMPTION at T={current_time}: {running_process.pid} (Priority {running_process.priority}) "
                         f"preempted {preempted.pid} (Priority {preempted.priority}).")
                tick_events.append(p_msg)
                events_log.append({"time": current_time, "type": "PREEMPT", "pid": running_process.pid, "message": p_msg})
                if running_process.start_time is None:
                    running_process.start_time = current_time
        else:
            if not heap.is_empty():
                running_process = heap.pop()
                if running_process.start_time is None:
                    running_process.start_time = current_time
                d_msg = f"CPU dispatched {running_process.pid} with highest priority ({running_process.priority})."
                tick_events.append(d_msg)
                events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": d_msg})

        if running_process is not None:
            decision_reason = f"Preemptive Priority: {running_process.pid} (Priority {running_process.priority}) has highest CPU priority."
        else:
            decision_reason = "CPU is idle (No ready processes in Min-Heap)."

        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "heap",
            "heap_metric_name": "Priority",
            "heap_snapshot": heap.get_snapshot(),
            "queue_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)

            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                c_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": c_msg})
                running_process = None
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "heap",
        "heap_metric_name": "Priority",
        "heap_snapshot": [],
        "queue_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, p.pid))
    return {
        "algorithm": "Preemptive Priority",
        "algorithm_key": "priority_preemptive",
        "category": "Preemptive",
        "data_structure": "Min-Heap (key: Priority)",
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time)
    }


# ==============================================================================
# 4. FIRST-COME, FIRST-SERVED (NON-PREEMPTIVE, FIFO QUEUE)
# ==============================================================================
def schedule_fcfs(processes: List[Process]) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    # Sort processes by arrival time initially to enqueue smoothly
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    queue = FIFOQueue()
    total_processes = len(procs)
    completed_processes: List[Process] = []

    current_time = 0
    running_process: Optional[Process] = None

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        # 1. New process arrivals (sorted deterministically)
        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                queue.enqueue(arr_proc)
                msg = f"Process {arr_proc.pid} arrived at T={current_time} -> Enqueued into FIFO Queue."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        # Non-preemptive: if CPU is idle, dispatch head of queue
        if running_process is None and not queue.is_empty():
            running_process = queue.dequeue()
            if running_process.start_time is None:
                running_process.start_time = current_time
            d_msg = f"FCFS dispatched {running_process.pid} (First in arrival order) to run until completion."
            tick_events.append(d_msg)
            events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": d_msg})

        if running_process is not None:
            decision_reason = f"FCFS: {running_process.pid} is running non-preemptively (Remaining: {running_process.remaining_time} units)."
        else:
            decision_reason = "CPU is idle (Waiting for process arrival in FIFO Queue)."

        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "queue",
            "queue_snapshot": queue.get_snapshot(),
            "heap_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)

            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                c_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": c_msg})
                running_process = None
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "queue",
        "queue_snapshot": [],
        "heap_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
    return {
        "algorithm": "First-Come, First-Served (FCFS)",
        "algorithm_key": "fcfs",
        "category": "Non-Preemptive",
        "data_structure": "FIFO Queue",
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time)
    }


# ==============================================================================
# 5. SHORTEST JOB FIRST (NON-PREEMPTIVE, MIN-HEAP KEYED BY BURST TIME)
# ==============================================================================
def schedule_sjf(processes: List[Process]) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    heap = MinHeap(key_func=lambda p: (p.burst_time, p.arrival_time, pid_sort_key(p.pid)))
    total_processes = len(procs)
    completed_processes: List[Process] = []

    current_time = 0
    running_process: Optional[Process] = None

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                heap.push(arr_proc)
                msg = f"Process {arr_proc.pid} arrived (Burst: {arr_proc.burst_time}) -> Pushed into SJF Min-Heap."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        # Non-preemptive: if idle, pop process with minimum initial burst time
        if running_process is None and not heap.is_empty():
            running_process = heap.pop()
            if running_process.start_time is None:
                running_process.start_time = current_time
            d_msg = f"SJF dispatched {running_process.pid} (Shortest Burst Time: {running_process.burst_time}) from Min-Heap."
            tick_events.append(d_msg)
            events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": d_msg})

        if running_process is not None:
            decision_reason = f"SJF: {running_process.pid} running to completion (Burst: {running_process.burst_time}, Remaining: {running_process.remaining_time})."
        else:
            decision_reason = "CPU is idle (No ready processes in SJF Min-Heap)."

        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "heap",
            "heap_metric_name": "Burst Time",
            "heap_snapshot": heap.get_snapshot(),
            "queue_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)

            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                c_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": c_msg})
                running_process = None
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "heap",
        "heap_metric_name": "Burst Time",
        "heap_snapshot": [],
        "queue_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
    return {
        "algorithm": "Shortest Job First (SJF)",
        "algorithm_key": "sjf",
        "category": "Non-Preemptive",
        "data_structure": "Min-Heap (key: Burst Time)",
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time)
    }


# ==============================================================================
# 6. NON-PREEMPTIVE PRIORITY SCHEDULING (MIN-HEAP KEYED BY PRIORITY)
# ==============================================================================
def schedule_priority_non_preemptive(processes: List[Process]) -> Dict[str, Any]:
    procs = [p.clone() for p in processes]
    arrivals: Dict[int, List[Process]] = {}
    for p in procs:
        arrivals.setdefault(p.arrival_time, []).append(p)

    heap = MinHeap(key_func=lambda p: (p.priority, p.arrival_time, pid_sort_key(p.pid)))
    total_processes = len(procs)
    completed_processes: List[Process] = []

    current_time = 0
    running_process: Optional[Process] = None

    gantt_units: List[Dict[str, Any]] = []
    events_log: List[Dict[str, Any]] = []
    time_steps: List[Dict[str, Any]] = []

    max_time_limit = sum(p.burst_time for p in procs) + max(p.arrival_time for p in procs) + 100

    while len(completed_processes) < total_processes and current_time < max_time_limit:
        tick_events: List[str] = []

        if current_time in arrivals:
            arrivals[current_time].sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
            for arr_proc in arrivals[current_time]:
                heap.push(arr_proc)
                msg = f"Process {arr_proc.pid} arrived (Priority: {arr_proc.priority}) -> Pushed into Priority Min-Heap."
                tick_events.append(msg)
                events_log.append({"time": current_time, "type": "ARRIVE", "pid": arr_proc.pid, "message": msg})

        # Non-preemptive: if idle, pop highest priority process
        if running_process is None and not heap.is_empty():
            running_process = heap.pop()
            if running_process.start_time is None:
                running_process.start_time = current_time
            d_msg = f"CPU dispatched {running_process.pid} (Priority {running_process.priority}) from Min-Heap."
            tick_events.append(d_msg)
            events_log.append({"time": current_time, "type": "DISPATCH", "pid": running_process.pid, "message": d_msg})

        if running_process is not None:
            decision_reason = f"Non-Preemptive Priority: {running_process.pid} running until finished (Priority: {running_process.priority}, Remaining: {running_process.remaining_time})."
        else:
            decision_reason = "CPU is idle (No ready processes in Min-Heap)."

        statuses = {}
        for p in procs:
            if p.is_completed():
                st = "COMPLETED"
            elif running_process and p.pid == running_process.pid:
                st = "RUNNING"
            elif p.arrival_time <= current_time:
                st = "READY"
            else:
                st = "NOT_ARRIVED"
            statuses[p.pid] = {
                "status": st,
                "remaining_time": p.remaining_time,
                "burst_time": p.burst_time,
                "completion_time": p.completion_time
            }

        snapshot = {
            "time": current_time,
            "running_pid": running_process.pid if running_process else None,
            "running_process": running_process.to_dict() if running_process else None,
            "ds_type": "heap",
            "heap_metric_name": "Priority",
            "heap_snapshot": heap.get_snapshot(),
            "queue_snapshot": [],
            "events": tick_events,
            "decision_reason": decision_reason,
            "process_statuses": statuses,
            "gantt_slice": _merge_gantt_blocks(gantt_units)
        }
        time_steps.append(snapshot)

        if running_process is not None:
            gantt_units.append({
                "pid": running_process.pid,
                "color": running_process.color,
                "start": current_time,
                "end": current_time + 1
            })
            running_process.execute_unit(current_time)

            if running_process.is_completed():
                running_process.finalize_metrics(current_time + 1)
                completed_processes.append(running_process)
                c_msg = f"Process {running_process.pid} completed at T={current_time + 1}."
                events_log.append({"time": current_time + 1, "type": "COMPLETE", "pid": running_process.pid, "message": c_msg})
                running_process = None
        else:
            gantt_units.append({
                "pid": "IDLE",
                "color": "#475569",
                "start": current_time,
                "end": current_time + 1
            })

        current_time += 1

    final_statuses = {p.pid: {"status": "COMPLETED", "remaining_time": 0, "burst_time": p.burst_time, "completion_time": p.completion_time} for p in procs}
    time_steps.append({
        "time": current_time,
        "running_pid": None,
        "running_process": None,
        "ds_type": "heap",
        "heap_metric_name": "Priority",
        "heap_snapshot": [],
        "queue_snapshot": [],
        "events": ["Simulation complete. All processes finished."],
        "decision_reason": "All processes completed execution.",
        "process_statuses": final_statuses,
        "gantt_slice": _merge_gantt_blocks(gantt_units)
    })

    completed_processes.sort(key=lambda p: (p.arrival_time, pid_sort_key(p.pid)))
    return {
        "algorithm": "Non-Preemptive Priority",
        "algorithm_key": "priority_non_preemptive",
        "category": "Non-Preemptive",
        "data_structure": "Min-Heap (key: Priority)",
        "total_time": current_time,
        "gantt_chart": _merge_gantt_blocks(gantt_units),
        "time_steps": time_steps,
        "events_log": events_log,
        "process_metrics": [p.to_dict() for p in completed_processes],
        "summary_metrics": _calculate_metrics(completed_processes, current_time)
    }


# Backward-compatibility aliases
schedule_preemptive = schedule_priority_preemptive
schedule_non_preemptive = schedule_priority_non_preemptive


def simulate_algorithm(algo_key: str, processes: List[Process], quantum: int = 2) -> Dict[str, Any]:
    """Unified dispatcher for all 6 scheduling algorithms."""
    algo_key = algo_key.lower().strip()
    if algo_key in ("round_robin", "rr"):
        return schedule_round_robin(processes, quantum)
    elif algo_key == "srtf":
        return schedule_srtf(processes)
    elif algo_key in ("priority_preemptive", "preemptive"):
        return schedule_priority_preemptive(processes)
    elif algo_key == "fcfs":
        return schedule_fcfs(processes)
    elif algo_key == "sjf":
        return schedule_sjf(processes)
    elif algo_key in ("priority_non_preemptive", "non-preemptive", "non_preemptive"):
        return schedule_priority_non_preemptive(processes)
    else:
        raise ValueError(f"Unknown scheduling algorithm '{algo_key}'.")


def compare_all_algorithms(processes: List[Process], quantum: int = 2) -> List[Dict[str, Any]]:
    """Runs all 6 algorithms on the same process dataset and returns comparative metrics."""
    algos = [
        ("fcfs", "First-Come, First-Served (FCFS)", "Non-Preemptive", "FIFO Queue"),
        ("sjf", "Shortest Job First (SJF)", "Non-Preemptive", "Min-Heap"),
        ("priority_non_preemptive", "Non-Preemptive Priority", "Non-Preemptive", "Min-Heap"),
        ("round_robin", f"Round Robin (Quantum={quantum})", "Preemptive", "FIFO Queue"),
        ("srtf", "Shortest Remaining Time First (SRTF)", "Preemptive", "Min-Heap"),
        ("priority_preemptive", "Preemptive Priority", "Preemptive", "Min-Heap")
    ]

    results = []
    for key, name, category, ds in algos:
        try:
            res = simulate_algorithm(key, processes, quantum)
            sum_met = res["summary_metrics"]
            results.append({
                "algorithm_key": key,
                "name": name,
                "category": category,
                "data_structure": ds,
                "avg_turnaround_time": sum_met["avg_turnaround_time"],
                "avg_waiting_time": sum_met["avg_waiting_time"],
                "avg_response_time": sum_met["avg_response_time"],
                "cpu_utilization": sum_met["cpu_utilization"],
                "throughput": sum_met["throughput"],
                "total_time": sum_met["total_time"]
            })
        except Exception:
            continue

    return results
