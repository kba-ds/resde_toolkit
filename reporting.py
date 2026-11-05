"""
Shared execution reporting for ResDE resource modules.

Records execution timestamps, duration, status, and captured output.
Uses only the Python standard library.
"""

from __future__ import annotations

import contextlib
import io
import json
import logging
import time
import traceback
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = REPORTS_DIR / "execution.log"
JSONL_FILE = REPORTS_DIR / "execution_reports.jsonl"

logger = logging.getLogger("resde.reporting")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False


def _write_report(report: dict[str, Any]) -> None:
    """Append one structured execution report as a JSON Lines record."""
    with JSONL_FILE.open("a", encoding="utf-8") as report_file:
        report_file.write(json.dumps(report, ensure_ascii=False) + "\n")


def run_reported(module_name: str, function: F, *args: Any, **kwargs: Any) -> Any:
    """
    Run a function, capture its printed output, and record its execution.

    The captured output is also echoed to the terminal. Exceptions are logged
    and re-raised so callers still see normal failure behavior.
    """
    started_at = datetime.now(timezone.utc)
    start_counter = time.perf_counter()
    captured = io.StringIO()
    status = "success"
    error_text = None
    result = None

    try:
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            result = function(*args, **kwargs)
    except Exception as exc:
        status = "failure"
        error_text = f"{type(exc).__name__}: {exc}"
        captured.write("\n" + traceback.format_exc())
    finally:
        duration_seconds = time.perf_counter() - start_counter
        finished_at = datetime.now(timezone.utc)
        output = captured.getvalue()

        report = {
            "module": module_name,
            "started_at_utc": started_at.isoformat(),
            "finished_at_utc": finished_at.isoformat(),
            "duration_seconds": round(duration_seconds, 6),
            "status": status,
            "output": output,
            "error": error_text,
        }
        _write_report(report)
        logger.info(
            "module=%s status=%s duration_seconds=%.6f",
            module_name,
            status,
            duration_seconds,
        )

        # Preserve the script's usual visible terminal output.
        if output:
            print(output, end="")

    if status == "failure":
        raise RuntimeError(
            f"ResDE module '{module_name}' failed: {error_text}"
        ) from None

    return result


def reported(module_name: str | None = None) -> Callable[[F], F]:
    """Decorator for a module's main function."""
    def decorator(function: F) -> F:
        name = module_name or function.__module__

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return run_reported(name, function, *args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
