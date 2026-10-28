
"""
RESDE Toolkit - Disk Diagnostics

Purpose:
    Monitor disk capacity, disk usage, partitions, and I/O activity.

Module:
    resde/diagnostics/disk.py
"""

from __future__ import annotations

from typing import Any
import psutil


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

WARNING_USAGE = 75.0
CRITICAL_USAGE = 90.0


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def _health_status(percent_used: float) -> str:
    """Return disk health status based on percentage used."""

    if percent_used >= CRITICAL_USAGE:
        return "CRITICAL"

    if percent_used >= WARNING_USAGE:
        return "WARNING"

    return "HEALTHY"


# ---------------------------------------------------------------------
# Disk capacity
# ---------------------------------------------------------------------

def get_disk_usage(path: str = "/") -> dict[str, Any]:
    """
    Return disk usage information for a specified path.
    """

    usage = psutil.disk_usage(path)

    percent_used = usage.percent

    return {
        "path": path,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "percent_used": percent_used,
        "percent_free": round(100 - percent_used, 2),
        "status": _health_status(percent_used),
    }


# ---------------------------------------------------------------------
# Disk partitions
# ---------------------------------------------------------------------

def get_partitions() -> list[dict[str, Any]]:
    """
    Return information about mounted disk partitions.
    """

    partitions = []

    for partition in psutil.disk_partitions(all=False):

        try:
            usage = psutil.disk_usage(partition.mountpoint)

            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "percent_used": usage.percent,
                "status": _health_status(usage.percent),
            })

        except (PermissionError, OSError):
            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "status": "UNAVAILABLE",
            })

    return partitions


# ---------------------------------------------------------------------
# Disk I/O
# ---------------------------------------------------------------------

def get_disk_io() -> dict[str, Any]:
    """
    Return cumulative disk I/O statistics.
    """

    io = psutil.disk_io_counters()

    if io is None:
        return {
            "status": "UNAVAILABLE"
        }

    return {
        "read_count": io.read_count,
        "write_count": io.write_count,
        "read_bytes": io.read_bytes,
        "write_bytes": io.write_bytes,
        "read_time_ms": io.read_time,
        "write_time_ms": io.write_time,
        "status": "AVAILABLE",
    }


# ---------------------------------------------------------------------
# Complete disk diagnostic
# ---------------------------------------------------------------------

def diagnose(path: str = "/") -> dict[str, Any]:
    """
    Run a complete disk diagnostic.
    """

    usage = get_disk_usage(path)
    partitions = get_partitions()
    io = get_disk_io()

    statuses = [
        partition.get("status")
        for partition in partitions
        if partition.get("status")
    ]

    statuses.append(usage["status"])

    if "CRITICAL" in statuses:
        overall_status = "CRITICAL"

    elif "WARNING" in statuses:
        overall_status = "WARNING"

    else:
        overall_status = "HEALTHY"

    return {
        "component": "disk",
        "overall_status": overall_status,
        "usage": usage,
        "partitions": partitions,
        "io": io,
    }


if __name__ == "__main__":
    import json

    result = diagnose()

    print(json.dumps(result, indent=4))