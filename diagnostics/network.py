
"""
RESDE Toolkit - Network Diagnostics

Purpose:
    Monitor network interfaces, addresses, traffic and connectivity.

Module:
    resde/diagnostics/network.py
"""

from __future__ import annotations

from typing import Any
import socket
import psutil


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DEFAULT_TEST_HOST = "8.8.8.8"
DEFAULT_TEST_PORT = 53
DEFAULT_TIMEOUT = 2.0


# ---------------------------------------------------------------------
# Network interfaces
# ---------------------------------------------------------------------

def get_interfaces() -> list[dict[str, Any]]:
    """
    Return information about network interfaces.
    """

    interfaces = []

    addresses = psutil.net_if_addrs()
    statistics = psutil.net_if_stats()

    for interface, addr_list in addresses.items():

        stats = statistics.get(interface)

        ipv4_addresses = []
        ipv6_addresses = []
        mac_address = None

        for address in addr_list:

            if address.family == socket.AF_INET:
                ipv4_addresses.append(address.address)

            elif address.family == socket.AF_INET6:
                ipv6_addresses.append(address.address)

            elif getattr(psutil, "AF_LINK", None) == address.family:
                mac_address = address.address

        interfaces.append({
            "interface": interface,
            "is_up": stats.isup if stats else None,
            "speed_mbps": stats.speed if stats else None,
            "mtu": stats.mtu if stats else None,
            "ipv4": ipv4_addresses,
            "ipv6": ipv6_addresses,
            "mac_address": mac_address,
        })

    return interfaces


# ---------------------------------------------------------------------
# Network traffic
# ---------------------------------------------------------------------

def get_network_io() -> dict[str, Any]:
    """
    Return cumulative network traffic statistics.
    """

    io = psutil.net_io_counters()

    return {
        "bytes_sent": io.bytes_sent,
        "bytes_received": io.bytes_recv,
        "packets_sent": io.packets_sent,
        "packets_received": io.packets_recv,
        "errors_in": io.errin,
        "errors_out": io.errout,
        "drops_in": io.dropin,
        "drops_out": io.dropout,
    }


# ---------------------------------------------------------------------
# Connectivity test
# ---------------------------------------------------------------------

def check_connectivity(
    host: str = DEFAULT_TEST_HOST,
    port: int = DEFAULT_TEST_PORT,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """
    Perform a basic TCP connectivity test.
    """

    try:

        with socket.create_connection(
            (host, port),
            timeout=timeout
        ):

            return {
                "host": host,
                "port": port,
                "reachable": True,
                "status": "HEALTHY",
            }

    except (socket.timeout, OSError) as error:

        return {
            "host": host,
            "port": port,
            "reachable": False,
            "status": "CRITICAL",
            "error": str(error),
        }


# ---------------------------------------------------------------------
# Complete network diagnostic
# ---------------------------------------------------------------------

def diagnose(
    host: str = DEFAULT_TEST_HOST,
    port: int = DEFAULT_TEST_PORT,
) -> dict[str, Any]:
    """
    Run a complete network diagnostic.
    """

    interfaces = get_interfaces()
    traffic = get_network_io()
    connectivity = check_connectivity(host, port)

    active_interfaces = [
        interface
        for interface in interfaces
        if interface.get("is_up") is True
    ]

    if not active_interfaces:
        overall_status = "CRITICAL"

    elif not connectivity["reachable"]:
        overall_status = "WARNING"

    else:
        overall_status = "HEALTHY"

    return {
        "component": "network",
        "overall_status": overall_status,
        "interfaces": interfaces,
        "active_interface_count": len(active_interfaces),
        "traffic": traffic,
        "connectivity": connectivity,
    }


if __name__ == "__main__":
    import json

    result = diagnose()

    print(json.dumps(result, indent=4))