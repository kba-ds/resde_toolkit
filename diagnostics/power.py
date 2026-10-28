
"""
RESDE Toolkit - Power Diagnostics

Purpose:
    Monitor battery status, charge level, power connection and
    estimated remaining battery time.

Module:
    resde/diagnostics/power.py
"""

from __future__ import annotations

from typing import Any
import psutil


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

WARNING_BATTERY = 30.0
CRITICAL_BATTERY = 15.0


# ---------------------------------------------------------------------
# Battery status
# ---------------------------------------------------------------------

def _battery_status(
    percent: float,
    plugged_in: bool,
) -> str:
    """
    Determine battery health status.
    """

    # A plugged-in laptop with low battery is not necessarily
    # in a critical state.
    if plugged_in:
        return "HEALTHY"

    if percent <= CRITICAL_BATTERY:
        return "CRITICAL"

    if percent <= WARNING_BATTERY:
        return "WARNING"

    return "HEALTHY"


def get_battery() -> dict[str, Any]:
    """
    Return battery information.
    """

    battery = psutil.sensors_battery()

    # Desktop computers may not have a battery.
    if battery is None:
        return {
            "available": False,
            "status": "NOT_APPLICABLE",
            "message": "No battery detected.",
        }

    seconds_left = battery.secsleft

    if seconds_left == psutil.POWER_TIME_UNLIMITED:
        time_remaining = None

    elif seconds_left == psutil.POWER_TIME_UNKNOWN:
        time_remaining = None

    else:
        time_remaining = seconds_left

    status = _battery_status(
        battery.percent,
        battery.power_plugged
    )

    return {
        "available": True,
        "percent": battery.percent,
        "power_plugged": battery.power_plugged,
        "seconds_remaining": time_remaining,
        "status": status,
    }


# ---------------------------------------------------------------------
# Power diagnostic
# ---------------------------------------------------------------------

def diagnose() -> dict[str, Any]:
    """
    Run a complete power diagnostic.
    """

    battery = get_battery()

    return {
        "component": "power",
        "overall_status": battery["status"],
        "battery": battery,
    }


if __name__ == "__main__":
    import json

    result = diagnose()

    print(json.dumps(result, indent=4))