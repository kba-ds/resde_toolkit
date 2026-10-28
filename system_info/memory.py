

"""
RESDE - Memory Diagnostics

Collects RAM and swap information for the
Resilient Python Data Engineering Toolkit.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import psutil


def bytes_to_gb(value: int) -> float:
    """
    Convert bytes to gigabytes.
    """

    return round(value / (1024 ** 3), 2)


def get_memory_info() -> dict[str, Any]:
    """
    Collect system memory information.
    """

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),

        # RAM
        "total_gb": bytes_to_gb(memory.total),
        "available_gb": bytes_to_gb(memory.available),
        "used_gb": bytes_to_gb(memory.used),
        "memory_percent": memory.percent,

        # Swap
        "swap_total_gb": bytes_to_gb(swap.total),
        "swap_used_gb": bytes_to_gb(swap.used),
        "swap_free_gb": bytes_to_gb(swap.free),
        "swap_percent": swap.percent,
    }


def classify_memory_pressure(
    memory_percent: float,
    swap_percent: float
) -> str:
    """
    Classify memory pressure using RAM and swap utilization.
    """

    if memory_percent < 60 and swap_percent < 20:
        return "low"

    if memory_percent < 75 and swap_percent < 40:
        return "moderate"

    if memory_percent < 90 and swap_percent < 70:
        return "high"

    return "critical"


def diagnose_memory() -> dict[str, Any]:
    """
    Run memory diagnostics and return a structured result.
    """

    info = get_memory_info()

    info["pressure"] = classify_memory_pressure(
        info["memory_percent"],
        info["swap_percent"]
    )

    return info


if __name__ == "__main__":
    import json

    result = diagnose_memory()

    print(
        json.dumps(
            result,
            indent=4
        )
    )