# """
# tests/test_scheduler.py
# Comprehensive automated test suite for CPU Scheduling Lab.

# Verifies:
# 1. Process Model (natural PID sort key, lifecycle metrics: CT, TAT, WT, RT).
# 2. Custom Data Structures (MinHeap and FIFOQueue, without heapq or queue module).
# 3. Input Validation (empty, duplicates, missing, negative, decimals, booleans, limits).
# 4. All Six Scheduling Algorithms:
#    - FCFS (Arrival order, convoy effect, non-preemptive, P2 vs P10 tie-breaking)
#    - SJF (Shortest original burst time, non-preemptive, tie-breaking)
#    - SRTF (Shortest remaining execution time, valid preemptions, resumes)
#    - Round Robin (FIFO time slicing, quantum expiration, arrivals at quantum boundary)
#    - Preemptive Priority (Lower number = higher priority, preemptions)
#    - Non-Preemptive Priority (Runs to completion, priority queue selection)
# 5. Metric calculations & Gantt chart intervals (CPU utilization, throughput, idle exclusion).
# 6. Flask API endpoints (/api/simulate, /api/compare, /api/presets, HTTP 400 on invalid input).
# """

# import unittest
# import json
# from scheduler.process import Process, pid_sort_key
# from scheduler.data_structures import MinHeap, FIFOQueue
# from scheduler.algorithms import (
#     validate_processes,
#     schedule_round_robin,
#     schedule_srtf,
#     schedule_priority_preemptive,
#     schedule_fcfs,
#     schedule_sjf,
#     schedule_priority_non_preemptive,
#     simulate_algorithm,
#     compare_all_algorithms
# )
# from app import app


# class TestProcessModel(unittest.TestCase):
#     def test_pid_sort_key(self):
#         # Numeric natural sorting: P2 must sort before P10
#         self.assertLess(pid_sort_key("P2"), pid_sort_key("P10"))
#         self.assertLess(pid_sort_key("P1"), pid_sort_key("P2"))
#         self.assertLess(pid_sort_key("P9"), pid_sort_key("P10"))
#         self.assertLess(pid_sort_key("TASK1"), pid_sort_key("TASK20"))
#         self.assertEqual(pid_sort_key("P5"), ("P", 5, ""))

#     def test_process_metrics_calculation(self):
#         p = Process(pid="P1", arrival_time=2, burst_time=6, priority=1)
#         self.assertEqual(p.remaining_time, 6)
#         self.assertFalse(p.is_completed())

#         # Start at T=3
#         p.execute_unit(current_time=3)
#         self.assertEqual(p.start_time, 3)
#         self.assertEqual(p.remaining_time, 5)

#         # Complete at T=9
#         for t in range(4, 9):
#             p.execute_unit(current_time=t)
#         self.assertTrue(p.is_completed())

#         p.finalize_metrics(completion_time=9)
#         self.assertEqual(p.completion_time, 9)
#         self.assertEqual(p.turnaround_time, 7)  # CT (9) - AT (2) = 7
#         self.assertEqual(p.waiting_time, 1)     # TAT (7) - BT (6) = 1
#         self.assertEqual(p.response_time, 1)    # ST (3) - AT (2) = 1


# class TestCustomDataStructures(unittest.TestCase):
#     def test_min_heap_operations(self):
#         heap = MinHeap(key_func=lambda p: (p.priority, p.arrival_time, pid_sort_key(p.pid)))
#         self.assertTrue(heap.is_empty())
#         self.assertEqual(heap.size(), 0)
#         self.assertIsNone(heap.peek())
#         self.assertIsNone(heap.pop())

#         # Insert out of order
#         p_low = Process("P3", arrival_time=0, burst_time=3, priority=5)
#         p_mid = Process("P10", arrival_time=0, burst_time=3, priority=2)
#         p_high = Process("P2", arrival_time=0, burst_time=3, priority=2)  # Same priority as P10, but P2 < P10
#         p_top = Process("P1", arrival_time=0, burst_time=3, priority=1)

#         heap.push(p_low)
#         heap.push(p_mid)
#         heap.push(p_high)
#         heap.push(p_top)

#         self.assertEqual(heap.size(), 4)
#         # Root must be P1 (Priority 1)
#         self.assertEqual(heap.peek().pid, "P1")
#         self.assertEqual(heap.pop().pid, "P1")

#         # Next must be P2 (Priority 2, P2 < P10 tie-breaker)
#         self.assertEqual(heap.pop().pid, "P2")

#         # Next is P10
#         self.assertEqual(heap.pop().pid, "P10")

#         # Last is P3 (Priority 5)
#         self.assertEqual(heap.pop().pid, "P3")
#         self.assertTrue(heap.is_empty())

#     def test_min_heap_snapshots(self):
#         heap = MinHeap()
#         p1 = Process("P1", arrival_time=0, burst_time=4, priority=2)
#         heap.push(p1)
#         snapshot = heap.get_snapshot()
#         self.assertEqual(len(snapshot), 1)
#         self.assertEqual(snapshot[0]["pid"], "P1")

#     def test_fifo_queue_operations(self):
#         queue = FIFOQueue()
#         self.assertTrue(queue.is_empty())
#         self.assertEqual(queue.size(), 0)
#         self.assertIsNone(queue.peek())
#         self.assertIsNone(queue.dequeue())

#         p1 = Process("P1", arrival_time=0, burst_time=2, priority=1)
#         p2 = Process("P2", arrival_time=1, burst_time=4, priority=2)
#         p3 = Process("P3", arrival_time=2, burst_time=1, priority=3)

#         queue.enqueue(p1)
#         queue.enqueue(p2)
#         queue.enqueue(p3)

#         self.assertEqual(queue.size(), 3)
#         self.assertEqual(queue.peek().pid, "P1")
#         self.assertEqual(queue.dequeue().pid, "P1")
#         self.assertEqual(queue.dequeue().pid, "P2")
#         self.assertEqual(queue.dequeue().pid, "P3")
#         self.assertTrue(queue.is_empty())


# class TestInputValidation(unittest.TestCase):
#     def test_empty_process_list(self):
#         is_valid, err, _, _ = validate_processes([])
#         self.assertFalse(is_valid)
#         self.assertIn("required", err.lower())

#     def test_non_list_input(self):
#         is_valid, err, _, _ = validate_processes("not-a-list")  # type: ignore
#         self.assertFalse(is_valid)

#     def test_missing_and_empty_pid(self):
#         data = [{"pid": "", "arrival_time": 0, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("empty Process ID", err)

#     def test_duplicate_pid(self):
#         data = [
#             {"pid": "P1", "arrival_time": 0, "burst_time": 3, "priority": 1},
#             {"pid": "p1", "arrival_time": 1, "burst_time": 2, "priority": 2}
#         ]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("Duplicate Process ID", err)

#     def test_negative_arrival_time(self):
#         data = [{"pid": "P1", "arrival_time": -2, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("Arrival Time", err)

#     def test_zero_and_negative_burst_time(self):
#         data = [{"pid": "P1", "arrival_time": 0, "burst_time": 0, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("Burst Time", err)

#     def test_decimals_and_booleans_rejected(self):
#         data = [{"pid": "P1", "arrival_time": 0.5, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("decimal", err)

#         data_bool = [{"pid": "P1", "arrival_time": True, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data_bool)
#         self.assertFalse(is_valid)
#         self.assertIn("boolean", err)

#     def test_limits_exceeded(self):
#         data = [{"pid": "P1", "arrival_time": 99999, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data)
#         self.assertFalse(is_valid)
#         self.assertIn("limit", err.lower())

#     def test_invalid_quantum(self):
#         data = [{"pid": "P1", "arrival_time": 0, "burst_time": 3, "priority": 1}]
#         is_valid, err, _, _ = validate_processes(data, quantum=0)
#         self.assertFalse(is_valid)

#         is_valid, err, _, _ = validate_processes(data, quantum=200)
#         self.assertFalse(is_valid)


# class TestAllSixAlgorithms(unittest.TestCase):
#     def test_1_fcfs_execution(self):
#         """
#         FCFS: Runs strictly in arrival order non-preemptively.
#         P1(AT=0, BT=4) -> runs [0-4], CT=4, TAT=4, WT=0, RT=0
#         P2(AT=2, BT=3) -> runs [4-7], CT=7, TAT=5, WT=2, RT=2
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=4, priority=2),
#             Process("P2", arrival_time=2, burst_time=3, priority=1)
#         ]
#         res = schedule_fcfs(procs)
#         self.assertEqual(res["total_time"], 7)
#         metrics = {p["pid"]: p for p in res["process_metrics"]}
#         self.assertEqual(metrics["P1"]["completion_time"], 4)
#         self.assertEqual(metrics["P1"]["waiting_time"], 0)
#         self.assertEqual(metrics["P2"]["completion_time"], 7)
#         self.assertEqual(metrics["P2"]["waiting_time"], 2)

#     def test_1_fcfs_tie_breaking(self):
#         """FCFS with simultaneous arrival: P2 and P10 arrive at T=0. P2 must precede P10."""
#         procs = [
#             Process("P10", arrival_time=0, burst_time=2, priority=1),
#             Process("P2", arrival_time=0, burst_time=2, priority=1)
#         ]
#         res = schedule_fcfs(procs)
#         gantt = res["gantt_chart"]
#         self.assertEqual(gantt[0]["pid"], "P2")
#         self.assertEqual(gantt[1]["pid"], "P10")

#     def test_2_sjf_execution(self):
#         """
#         SJF: Once CPU becomes free at T=3, picks process with shortest initial burst.
#         P1(AT=0, BT=3) -> runs [0-3]
#         At T=3: P2(AT=1, BT=5) and P3(AT=2, BT=1) are ready.
#         SJF must choose P3 (BT=1) before P2 (BT=5).
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=3, priority=3),
#             Process("P2", arrival_time=1, burst_time=5, priority=1),
#             Process("P3", arrival_time=2, burst_time=1, priority=2)
#         ]
#         res = schedule_sjf(procs)
#         gantt = res["gantt_chart"]
#         self.assertEqual([b["pid"] for b in gantt], ["P1", "P3", "P2"])
#         metrics = {p["pid"]: p for p in res["process_metrics"]}
#         self.assertEqual(metrics["P3"]["completion_time"], 4)
#         self.assertEqual(metrics["P2"]["completion_time"], 9)

#     def test_3_srtf_preemption(self):
#         """
#         SRTF: Arriving process with strictly shorter remaining time preempts running process.
#         P1(AT=0, BT=8): runs [0-1], remaining=7.
#         P2(AT=1, BT=2): arrives with BT=2 < 7 -> Preempts P1! Runs [1-3], finishes at T=3.
#         P1 resumes [3-10], finishes at T=10.
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=8, priority=2),
#             Process("P2", arrival_time=1, burst_time=2, priority=1)
#         ]
#         res = schedule_srtf(procs)
#         gantt = res["gantt_chart"]
#         self.assertEqual([b["pid"] for b in gantt], ["P1", "P2", "P1"])
#         self.assertEqual(gantt[0]["end"], 1)
#         self.assertEqual(gantt[1]["start"], 1)
#         self.assertEqual(gantt[1]["end"], 3)
#         self.assertEqual(gantt[2]["start"], 3)
#         self.assertEqual(gantt[2]["end"], 10)

#     def test_4_round_robin_execution(self):
#         """
#         Round Robin (Q=2):
#         P1(AT=0, BT=5), P2(AT=1, BT=3).
#         T=0..2: P1 runs (slice=2, rem=3). At T=1, P2 arrived into queue.
#         At T=2: P1 quantum expires, re-enqueued behind P2. Queue=[P2, P1].
#         T=2..4: P2 runs (slice=2, rem=1).
#         T=4..6: P1 runs (slice=2, rem=1).
#         T=6..7: P2 runs (slice=1, rem=0) -> finishes at T=7.
#         T=7..8: P1 runs (slice=1, rem=0) -> finishes at T=8.
#         Total time = 8. No trailing idle unit!
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=5, priority=1),
#             Process("P2", arrival_time=1, burst_time=3, priority=2)
#         ]
#         res = schedule_round_robin(procs, quantum=2)
#         self.assertEqual(res["total_time"], 8)
#         self.assertEqual(res["summary_metrics"]["idle_time"], 0)
#         self.assertEqual(res["summary_metrics"]["cpu_utilization"], 100.0)
#         metrics = {p["pid"]: p for p in res["process_metrics"]}
#         self.assertEqual(metrics["P2"]["completion_time"], 7)
#         self.assertEqual(metrics["P1"]["completion_time"], 8)

#     def test_5_preemptive_priority(self):
#         """
#         Preemptive Priority:
#         P1(AT=0, BT=6, Prio=3): runs [0-2].
#         P2(AT=2, BT=2, Prio=1): arrives with Prio 1 < 3 -> Preempts P1! Runs [2-4].
#         P1 resumes [4-8].
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=6, priority=3),
#             Process("P2", arrival_time=2, burst_time=2, priority=1)
#         ]
#         res = schedule_priority_preemptive(procs)
#         gantt = res["gantt_chart"]
#         self.assertEqual([b["pid"] for b in gantt], ["P1", "P2", "P1"])
#         metrics = {p["pid"]: p for p in res["process_metrics"]}
#         self.assertEqual(metrics["P2"]["completion_time"], 4)
#         self.assertEqual(metrics["P1"]["completion_time"], 8)

#     def test_6_non_preemptive_priority(self):
#         """
#         Non-Preemptive Priority:
#         P1(AT=0, BT=4, Prio=3) starts at T=0.
#         P2(AT=1, BT=2, Prio=1) arrives at T=1 with higher priority.
#         P1 MUST NOT be preempted, runs until completion at T=4.
#         P2 runs [4-6].
#         """
#         procs = [
#             Process("P1", arrival_time=0, burst_time=4, priority=3),
#             Process("P2", arrival_time=1, burst_time=2, priority=1)
#         ]
#         res = schedule_priority_non_preemptive(procs)
#         gantt = res["gantt_chart"]
#         self.assertEqual([b["pid"] for b in gantt], ["P1", "P2"])
#         metrics = {p["pid"]: p for p in res["process_metrics"]}
#         self.assertEqual(metrics["P1"]["completion_time"], 4)
#         self.assertEqual(metrics["P2"]["completion_time"], 6)

#     def test_idle_periods_handling(self):
#         """CPU idle intervals between spaced process arrivals."""
#         procs = [
#             Process("P1", arrival_time=1, burst_time=2, priority=1),
#             Process("P2", arrival_time=6, burst_time=2, priority=1)
#         ]
#         res = schedule_fcfs(procs)
#         gantt = res["gantt_chart"]
#         # [0-1] IDLE, [1-3] P1, [3-6] IDLE, [6-8] P2
#         self.assertEqual(gantt[0]["pid"], "IDLE")
#         self.assertEqual(gantt[0]["start"], 0)
#         self.assertEqual(gantt[0]["end"], 1)

#         self.assertEqual(gantt[1]["pid"], "P1")
#         self.assertEqual(gantt[1]["start"], 1)
#         self.assertEqual(gantt[1]["end"], 3)

#         self.assertEqual(gantt[2]["pid"], "IDLE")
#         self.assertEqual(gantt[2]["start"], 3)
#         self.assertEqual(gantt[2]["end"], 6)

#         self.assertEqual(gantt[3]["pid"], "P2")
#         self.assertEqual(gantt[3]["start"], 6)
#         self.assertEqual(gantt[3]["end"], 8)

#         # Idle time = 1 + 3 = 4; Busy time = 4; Total time = 8; Util = 50%
#         self.assertEqual(res["summary_metrics"]["idle_time"], 4)
#         self.assertEqual(res["summary_metrics"]["cpu_utilization"], 50.0)

#     def test_compare_all_algorithms(self):
#         procs = [
#             Process("P1", arrival_time=0, burst_time=4, priority=2),
#             Process("P2", arrival_time=1, burst_time=2, priority=1)
#         ]
#         comparison = compare_all_algorithms(procs, quantum=2)
#         self.assertEqual(len(comparison), 6)
#         keys = [item["algorithm_key"] for item in comparison]
#         self.assertIn("fcfs", keys)
#         self.assertIn("sjf", keys)
#         self.assertIn("priority_non_preemptive", keys)
#         self.assertIn("round_robin", keys)
#         self.assertIn("srtf", keys)
#         self.assertIn("priority_preemptive", keys)


# class TestFlaskEndpoints(unittest.TestCase):
#     def setUp(self):
#         self.client = app.test_client()

#     def test_api_presets(self):
#         res = self.client.get("/api/presets")
#         self.assertEqual(res.status_code, 200)
#         data = res.get_json()
#         self.assertTrue(data["success"])
#         self.assertIn("round_robin_demo", data["presets"])

#     def test_api_simulate_success(self):
#         payload = {
#             "algorithm": "round_robin",
#             "quantum": 2,
#             "processes": [
#                 {"pid": "P1", "arrival_time": 0, "burst_time": 3, "priority": 1},
#                 {"pid": "P2", "arrival_time": 1, "burst_time": 2, "priority": 2}
#             ]
#         }
#         res = self.client.post("/api/simulate", data=json.dumps(payload), content_type="application/json")
#         self.assertEqual(res.status_code, 200)
#         data = res.get_json()
#         self.assertTrue(data["success"])
#         self.assertEqual(data["data"]["algorithm_key"], "round_robin")

#     def test_api_simulate_invalid_input_status_400(self):
#         payload = {
#             "algorithm": "round_robin",
#             "quantum": 2,
#             "processes": []
#         }
#         res = self.client.post("/api/simulate", data=json.dumps(payload), content_type="application/json")
#         self.assertEqual(res.status_code, 400)
#         data = res.get_json()
#         self.assertFalse(data["success"])

#     def test_api_simulate_malformed_json_status_400(self):
#         res = self.client.post("/api/simulate", data="{malformed_json", content_type="application/json")
#         self.assertEqual(res.status_code, 400)

#     def test_api_compare_success(self):
#         payload = {
#             "processes": [
#                 {"pid": "P1", "arrival_time": 0, "burst_time": 4, "priority": 1},
#                 {"pid": "P2", "arrival_time": 1, "burst_time": 2, "priority": 2}
#             ],
#             "quantum": 2
#         }
#         res = self.client.post("/api/compare", data=json.dumps(payload), content_type="application/json")
#         self.assertEqual(res.status_code, 200)
#         data = res.get_json()
#         self.assertTrue(data["success"])
#         self.assertEqual(len(data["comparison"]), 6)


# if __name__ == "__main__":
#     unittest.main()
