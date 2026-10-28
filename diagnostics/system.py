

"""
RESDE - System Diagnostics

Central system diagnostic module for the
Resilient Python Data Engineering Toolkit.

This module combines CPU and memory diagnostics
into a single system-level diagnostic report.
"""

from __future__ import annotations

import json
import platform
import socket
import sys
from datetime import datetime, timezone
from typing import Any

import psutil

from .cpu import diagnose_cpu
from .memory import diagnose_memory


def get_system_info() -> dict[str, Any]:
    """
    Collect general operating-system information.
    """

    boot_time = datetime.fromtimestamp(
        psutil.boot_time(),
        tz=timezone.utc
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "boot_time": boot_time.isoformat(),
    }


def determine_overall_pressure(
    cpu_pressure: str,
    memory_pressure: str
) -> str:
    """
    Determine overall system resource pressure.

    The most severe resource condition determines
    the overall pressure level.
    """

    severity = {
        "low": 1,
        "moderate": 2,
        "high": 3,
        "critical": 4,
    }

    pressure_levels = [
        cpu_pressure,
        memory_pressure
    ]

    return max(
        pressure_levels,
        key=lambda level: severity[level]
    )


def diagnose_system() -> dict[str, Any]:
    """
    Run the complete basic RESDE system diagnostic.
    """

    system = get_system_info()
    cpu = diagnose_cpu()
    memory = diagnose_memory()

    overall_pressure = determine_overall_pressure(
        cpu["pressure"],
        memory["pressure"]
    )

    return {
        "resde_version": "0.1.0",
        "diagnostic_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "system": system,

        "cpu": cpu,

        "memory": memory,

        "overall_pressure": overall_pressure,
    }


def print_diagnostics() -> None:
    """
    Print the diagnostic report in JSON format.
    """

    report = diagnose_system()

    print(
        json.dumps(
            report,
            indent=4
        )
    )


if __name__ == "__main__":
    print_diagnostics()