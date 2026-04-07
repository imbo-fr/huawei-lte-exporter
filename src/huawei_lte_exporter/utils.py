from __future__ import annotations
import re

_NUMERIC_RE = re.compile(r"[-+]?\d*\.?\d+")


def to_float(value: object, default: float = 0.0) -> float:
    """Convert router string values like '-95dBm', '20MHz' to float."""
    if value is None:
        return default
    m = _NUMERIC_RE.search(str(value).strip())
    if m:
        try:
            return float(m.group())
        except ValueError:
            pass
    return default


def connection_status_to_int(status: object) -> float:
    """901 = Connected → 1.0, anything else → 0.0."""
    return 1.0 if str(status) == "901" else 0.0
