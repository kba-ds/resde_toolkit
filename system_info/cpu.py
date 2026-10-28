

# in the first iteration of this script, there is a problem 
# line 21. 

"""
RESDE - CPU Diagnostics

Collects CPU-related system metrics for the
Resilient Python Data Engineering Toolkit.

Purpose:
    Observe CPU conditions and provide structured
    diagnostics for downstream RESDE decision-making.
"""

from __future__ import annotations

import os
import platform
from datetime import datetime, timezone
from typing import Any

import psutil


def get_cpu_info() -> dict[str, Any]:
    """
    Collect basic CPU information.

    Returns
    -------
    dict
        CPU hardware and utilization information.
    """

    cpu_percent = psutil.cpu_percent(interval=1)

    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)

    frequency = psutil.cpu_freq()

    # Load average is not available on every operating system.
    try:
        load_average = os.getloadavg()
    except (AttributeError, OSError):
        load_average = None

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "processor": platform.processor(),
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "cpu_percent": cpu_percent,
        "frequency_mhz": (
            round(frequency.current, 2)
            if frequency
            else None
        ),
        "load_average_1m": (
            round(load_average[0], 2)
            if load_average
            else None
        ),
        "load_average_5m": (
            round(load_average[1], 2)
            if load_average
            else None
        ),
        "load_average_15m": (
            round(load_average[2], 2)
            if load_average
            else None
        ),
    }


def classify_cpu_pressure(cpu_percent: float) -> str:
    """
    Classify CPU pressure.

    Parameters
    ----------
    cpu_percent : float
        Current CPU utilization percentage.

    Returns
    -------
    str
        CPU pressure category.
    """

    if cpu_percent < 50:
        return "low"

    if cpu_percent < 75:
        return "moderate"

    if cpu_percent < 90:
        return "high"

    return "critical"


def diagnose_cpu() -> dict[str, Any]:
    """
    Run CPU diagnostics and return a structured result.
    """

    info = get_cpu_info()

    info["pressure"] = classify_cpu_pressure(
        info["cpu_percent"]
    )

    return info


if __name__ == "__main__":
    import json

    result = diagnose_cpu()

    print(
        json.dumps(
            result,
            indent=4
        )
    )