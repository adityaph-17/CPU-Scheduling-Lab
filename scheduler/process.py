"""
scheduler/process.py
Defines the Process class representing an individual task to be scheduled by the CPU.
Includes attributes for priority scheduling, execution tracking, deterministic tie-breaking,
and metric calculation.
"""

import re
from typing import Optional, Dict, Any, Tuple


def pid_sort_key(pid: str) -> Tuple[str, int, str]:
    """
    Deterministic natural sort key for Process IDs.
    Splits PIDs like 'P2' into ('P', 2, '') and 'P10' into ('P', 10, ''),
    ensuring P2 sorts before P10 (numeric-aware sorting).
    Non-numeric PIDs fall back gracefully.
    """
    cleaned = str(pid).strip().upper()
    match = re.match(r"^([A-Z_-]*)(\d+)(.*)$", cleaned)
    if match:
        prefix, num, suffix = match.groups()
        return (prefix, int(num), suffix)
    return (cleaned, 0, "")


class Process:
    """
    Represents a process with its attributes and lifecycle metrics.
    Priority convention: Lower numerical value indicates higher priority (e.g., 1 is higher priority than 2).
    """

    def __init__(
        self,
        pid: str,
        arrival_time: int,
        burst_time: int,
        priority: int,
        color: Optional[str] = None
    ):
        self.pid: str = str(pid).strip().upper()
        self.arrival_time: int = int(arrival_time)
        self.burst_time: int = int(burst_time)
        self.priority: int = int(priority)
        self.remaining_time: int = int(burst_time)
        self.color: str = color or "#3b82f6"

        # Lifecycle metrics
        self.start_time: Optional[int] = None       # First time process gets CPU
        self.completion_time: Optional[int] = None  # Time at which process finishes
        self.turnaround_time: Optional[int] = None  # CT - AT
        self.waiting_time: Optional[int] = None     # TAT - BT
        self.response_time: Optional[int] = None    # ST - AT

    def is_completed(self) -> bool:
        """Returns True if the process has completed execution."""
        return self.remaining_time <= 0

    def execute_unit(self, current_time: int) -> None:
        """
        Executes the process for one time unit.
        Records start_time on initial execution.
        """
        if self.start_time is None:
            self.start_time = current_time
        if self.remaining_time > 0:
            self.remaining_time -= 1

    def finalize_metrics(self, completion_time: int) -> None:
        """Calculates final completion, turnaround, waiting, and response times."""
        self.completion_time = completion_time
        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time
        if self.start_time is not None:
            self.response_time = self.start_time - self.arrival_time
        else:
            self.response_time = 0

    def clone(self) -> "Process":
        """Creates a fresh copy of the process for simulation."""
        p = Process(
            pid=self.pid,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
            color=self.color
        )
        return p

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the process to a dictionary for API responses."""
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "remaining_time": self.remaining_time,
            "color": self.color,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time,
            "response_time": self.response_time,
            "is_completed": self.is_completed()
        }

    # Comparison methods for the Custom Min-Heap and tie-breaking:
    # 1. Primary: Priority (smaller is higher)
    # 2. Secondary: Earlier arrival time
    # 3. Tertiary: Deterministic numeric PID (e.g. P2 before P10)
    def __lt__(self, other: "Process") -> bool:
        if not isinstance(other, Process):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority < other.priority
        if self.arrival_time != other.arrival_time:
            return self.arrival_time < other.arrival_time
        return pid_sort_key(self.pid) < pid_sort_key(other.pid)

    def __le__(self, other: "Process") -> bool:
        if not isinstance(other, Process):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other: "Process") -> bool:
        if not isinstance(other, Process):
            return NotImplemented
        return not (self <= other)

    def __ge__(self, other: "Process") -> bool:
        if not isinstance(other, Process):
            return NotImplemented
        return not (self < other)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Process):
            return False
        return (
            self.priority == other.priority and
            self.arrival_time == other.arrival_time and
            pid_sort_key(self.pid) == pid_sort_key(other.pid)
        )

    def __repr__(self) -> str:
        return f"Process(PID={self.pid}, AT={self.arrival_time}, BT={self.burst_time}, Prio={self.priority}, Rem={self.remaining_time})"
