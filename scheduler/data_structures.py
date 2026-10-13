"""
scheduler/data_structures.py
Implements core Data Structures manually from scratch (no heapq or queue module):
1. MinHeap: Binary Min-Heap with custom key extraction for SJF, SRTF, and Priority.
2. FIFOQueue: Array-backed FIFO Queue for FCFS and Round Robin.
"""

from typing import List, Dict, Any, Optional, Callable
from scheduler.process import Process, pid_sort_key

class MinHeap:
    """
    A manual binary Min-Heap implementation backed by a Python list.
    Supports a custom key function for versatile sorting:
    - Priority Scheduling: key = (priority, arrival_time, pid_sort_key(pid))
    - SJF: key = (burst_time, arrival_time, pid_sort_key(pid))
    - SRTF: key = (remaining_time, arrival_time, pid_sort_key(pid))
    
    Tie-breaking rule:
    1. Primary metric (priority / burst / remaining)
    2. Earlier arrival time
    3. Natural numeric PID (e.g., P2 before P10)
    """

    def __init__(self, key_func: Optional[Callable[[Process], Any]] = None):
        self.heap: List[Process] = []
        # Default key comparator uses Process's natural order
        self.key_func = key_func if key_func is not None else (lambda p: (p.priority, p.arrival_time, pid_sort_key(p.pid)))

    def _get_key(self, proc: Process) -> Any:
        return self.key_func(proc)

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def size(self) -> int:
        return len(self.heap)

    def peek(self) -> Optional[Process]:
        if self.is_empty():
            return None
        return self.heap[0]

    def push(self, process: Process) -> None:
        """Inserts an element and restores min-heap property via sift-up. O(log N)"""
        self.heap.append(process)
        self._heapify_up(len(self.heap) - 1)

    def pop(self) -> Optional[Process]:
        """Extracts the root (minimum key) and restores min-heap property via sift-down. O(log N)"""
        if self.is_empty():
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index: int) -> None:
        parent_idx = (index - 1) // 2
        while index > 0 and self._get_key(self.heap[index]) < self._get_key(self.heap[parent_idx]):
            self.heap[index], self.heap[parent_idx] = self.heap[parent_idx], self.heap[index]
            index = parent_idx
            parent_idx = (index - 1) // 2

    def _heapify_down(self, index: int) -> None:
        n = len(self.heap)
        while True:
            smallest = index
            left_child = 2 * index + 1
            right_child = 2 * index + 2

            if left_child < n and self._get_key(self.heap[left_child]) < self._get_key(self.heap[smallest]):
                smallest = left_child

            if right_child < n and self._get_key(self.heap[right_child]) < self._get_key(self.heap[smallest]):
                smallest = right_child

            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break

    def get_snapshot(self) -> List[Dict[str, Any]]:
        """
        Returns structured data for visualization:
        Node index, parent index, child indices, and key metric.
        """
        snapshot = []
        n = len(self.heap)
        for i, proc in enumerate(self.heap):
            parent_idx = (i - 1) // 2 if i > 0 else None
            left_child = 2 * i + 1 if 2 * i + 1 < n else None
            right_child = 2 * i + 2 if 2 * i + 2 < n else None
            key_val = self._get_key(proc)

            snapshot.append({
                "index": i,
                "pid": proc.pid,
                "priority": proc.priority,
                "burst_time": proc.burst_time,
                "remaining_time": proc.remaining_time,
                "arrival_time": proc.arrival_time,
                "color": proc.color,
                "sort_key_display": str(key_val[0]),
                "parent_index": parent_idx,
                "left_child_index": left_child,
                "right_child_index": right_child
            })
        return snapshot

    def to_list(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.heap]


class FIFOQueue:
    """
    A manual First-In-First-Out (FIFO) Queue implementation for Round Robin and FCFS.
    Backing store is a Python list with clear O(1) front peek and O(N) dequeue (or pointer-based).
    Provides snapshots of Queue state for frontend visualization.
    """

    def __init__(self):
        self.items: List[Process] = []

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)

    def enqueue(self, process: Process) -> None:
        """Appends a process to the tail of the queue."""
        self.items.append(process)

    def dequeue(self) -> Optional[Process]:
        """Removes and returns the process from the head of the queue."""
        if self.is_empty():
            return None
        return self.items.pop(0)

    def peek(self) -> Optional[Process]:
        """Returns the process at the head without removal."""
        if self.is_empty():
            return None
        return self.items[0]

    def get_snapshot(self) -> List[Dict[str, Any]]:
        """
        Returns an ordered snapshot from Head to Tail for frontend queue display.
        """
        snapshot = []
        for i, proc in enumerate(self.items):
            snapshot.append({
                "position": i,
                "is_head": i == 0,
                "is_tail": i == len(self.items) - 1,
                "pid": proc.pid,
                "priority": proc.priority,
                "burst_time": proc.burst_time,
                "remaining_time": proc.remaining_time,
                "arrival_time": proc.arrival_time,
                "color": proc.color
            })
        return snapshot

    def to_list(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.items]
