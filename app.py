"""
app.py
Flask web server for CPU Scheduling Lab.
Connects the web frontend to the custom DSA scheduling engine.
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest
from scheduler import (
    validate_processes,
    simulate_algorithm,
    compare_all_algorithms
)

app = Flask(__name__)

# Educational Presets for college DSA demonstration
PRESETS = {
    "round_robin_demo": {
        "name": "Round Robin (Time Slicing)",
        "algorithm": "round_robin",
        "quantum": 2,
        "description": "Demonstrates cyclical time sharing via FIFO Queue with Quantum = 2.",
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2, "color": "#3b82f6"},
            {"pid": "P2", "arrival_time": 1, "burst_time": 4, "priority": 1, "color": "#ec4899"},
            {"pid": "P3", "arrival_time": 2, "burst_time": 2, "priority": 3, "color": "#10b981"},
            {"pid": "P4", "arrival_time": 3, "burst_time": 1, "priority": 4, "color": "#f59e0b"}
        ]
    },
    "srtf_preemption": {
        "name": "Shortest Remaining Time First (SRTF)",
        "algorithm": "srtf",
        "quantum": 2,
        "description": "Demonstrates preemptions whenever a process with shorter remaining burst arrives into the Min-Heap.",
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 8, "priority": 3, "color": "#3b82f6"},
            {"pid": "P2", "arrival_time": 1, "burst_time": 4, "priority": 1, "color": "#ec4899"},
            {"pid": "P3", "arrival_time": 2, "burst_time": 9, "priority": 4, "color": "#10b981"},
            {"pid": "P4", "arrival_time": 3, "burst_time": 2, "priority": 2, "color": "#f59e0b"}
        ]
    },
    "priority_preemptive_classic": {
        "name": "Preemptive Priority (Min-Heap)",
        "algorithm": "priority_preemptive",
        "quantum": 2,
        "description": "P2 (Priority 1) arrives at T=1 and preempts P1 (Priority 2).",
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 4, "priority": 2, "color": "#3b82f6"},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1, "color": "#ec4899"},
            {"pid": "P3", "arrival_time": 2, "burst_time": 1, "priority": 3, "color": "#10b981"},
            {"pid": "P4", "arrival_time": 3, "burst_time": 2, "priority": 4, "color": "#f59e0b"}
        ]
    },
    "fcfs_convoy": {
        "name": "FCFS (Convoy Effect)",
        "algorithm": "fcfs",
        "quantum": 2,
        "description": "A long CPU burst at T=0 delays short subsequent tasks in the FIFO Queue.",
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 10, "priority": 3, "color": "#3b82f6"},
            {"pid": "P2", "arrival_time": 1, "burst_time": 2, "priority": 1, "color": "#ec4899"},
            {"pid": "P3", "arrival_time": 2, "burst_time": 2, "priority": 2, "color": "#10b981"}
        ]
    },
    "sjf_optimal": {
        "name": "Shortest Job First (Non-Preemptive)",
        "algorithm": "sjf",
        "quantum": 2,
        "description": "Picks the shortest burst time using the Min-Heap once the CPU is free.",
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2, "color": "#3b82f6"},
            {"pid": "P2", "arrival_time": 1, "burst_time": 8, "priority": 1, "color": "#ec4899"},
            {"pid": "P3", "arrival_time": 2, "burst_time": 3, "priority": 4, "color": "#10b981"},
            {"pid": "P4", "arrival_time": 3, "burst_time": 2, "priority": 3, "color": "#f59e0b"}
        ]
    },
    "idle_gaps": {
        "name": "Spaced Arrivals & CPU Idle Intervals",
        "algorithm": "priority_preemptive",
        "quantum": 2,
        "description": "Demonstrates scheduler handling of intervals where no tasks are in the ready queue.",
        "processes": [
            {"pid": "P1", "arrival_time": 1, "burst_time": 2, "priority": 2, "color": "#06b6d4"},
            {"pid": "P2", "arrival_time": 5, "burst_time": 3, "priority": 1, "color": "#8b5cf6"},
            {"pid": "P3", "arrival_time": 10, "burst_time": 2, "priority": 3, "color": "#f97316"}
        ]
    }
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify({
        "success": True,
        "presets": PRESETS
    })


@app.route("/api/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        algorithm = str(data.get("algorithm", "priority_preemptive")).strip().lower()
        raw_processes = data.get("processes", [])
        quantum = data.get("quantum", 2)

        is_valid, error_msg, processes, val_quantum = validate_processes(raw_processes, quantum)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400

        result = simulate_algorithm(algorithm, processes, val_quantum)

        return jsonify({
            "success": True,
            "data": result
        })

    except BadRequest:
        return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Simulation server error: {str(e)}"}), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    """Runs all 6 scheduling algorithms on the same workload to compare their performance."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        raw_processes = data.get("processes", [])
        quantum = data.get("quantum", 2)

        is_valid, error_msg, processes, val_quantum = validate_processes(raw_processes, quantum)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400

        comparison_results = compare_all_algorithms(processes, val_quantum)

        return jsonify({
            "success": True,
            "comparison": comparison_results
        })

    except BadRequest:
        return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Comparison server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
