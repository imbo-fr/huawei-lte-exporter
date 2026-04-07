import pytest
from huawei_lte_exporter.utils import connection_status_to_int, to_float


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("-95dBm", -95.0),
        ("15dB", 15.0),
        ("20MHz", 20.0),
        ("4", 4.0),
        (None, 0.0),
        ("", 0.0),
        ("n/a", 0.0),
        (0, 0.0),
        (-12.5, -12.5),
        ("+23", 23.0),
    ],
)
def test_to_float(raw, expected):
    assert to_float(raw) == expected


@pytest.mark.parametrize(
    "status,expected",
    [
        ("901", 1.0),
        ("902", 0.0),
        ("905", 0.0),
        (901, 1.0),
        (None, 0.0),
    ],
)
def test_connection_status_to_int(status, expected):
    assert connection_status_to_int(status) == expected
