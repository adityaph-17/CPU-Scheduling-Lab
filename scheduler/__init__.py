"""
scheduler package
Exposes Process model, Custom Data Structures (MinHeap, FIFOQueue),
and all 6 CPU scheduling algorithms.
"""

from scheduler.process import Process
from scheduler.data_structures import MinHeap, FIFOQueue
from scheduler.algorithms import (
    validate_processes,
    simulate_algorithm,
    compare_all_algorithms,
    schedule_round_robin,
    schedule_srtf,
    schedule_priority_preemptive,
    schedule_fcfs,
    schedule_sjf,
    schedule_priority_non_preemptive,
    schedule_preemptive,
    schedule_non_preemptive
)

__all__ = [
    "Process",
    "MinHeap",
    "FIFOQueue",
    "validate_processes",
    "simulate_algorithm",
    "compare_all_algorithms",
    "schedule_round_robin",
    "schedule_srtf",
    "schedule_priority_preemptive",
    "schedule_fcfs",
    "schedule_sjf",
    "schedule_priority_non_preemptive",
    "schedule_preemptive",
    "schedule_non_preemptive"
]
