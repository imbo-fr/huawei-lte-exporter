from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
from huawei_lte_exporter.config import Config
from huawei_lte_exporter.collector import HuaweiLTECollector

SIGNAL_DATA = {
    "rssi": "-75dBm",
    "rsrp": "-95dBm",
    "rsrq": "-12dB",
    "sinr": "15dB",
    "rscp": None,
    "ecio": None,
    "band": "3",
    "cell_id": "12345678",
    "pci": "42",
    "earfcn": "1300",
    "dlbandwidth": "20MHz",
    "ulbandwidth": "20MHz",
    "txpower": "23",
    "dlmcs": "28",
    "ulmcs": "20",
    "nrdlmimolayers": "2",
    "mode": "7",
    "lac": "1001",
}
TRAFFIC_DATA = {
    "TotalDownload": "10737418240",
    "TotalUpload": "2147483648",
    "CurrentDownloadRate": "1048576",
    "CurrentUploadRate": "131072",
    "CurrentDownload": "536870912",
    "CurrentUpload": "67108864",
}
STATUS_DATA = {
    "SignalIcon": "4",
    "ConnectionStatus": "901",
    "RoamingStatus": "0",
    "CurrentNetworkType": "19",
}
PLMN_DATA = {"FullName": "Free Mobile", "ShortName": "Free", "Numeric": "20815"}
DEVICE_DATA = {
    "DeviceName": "B535-232",
    "SerialNumber": "SN12345678",
    "Imei": "123456789012345",
    "HardwareVersion": "WL2B310FM Ver.A",
    "SoftwareVersion": "11.0.1.2(H192SP1C983)",
    "UpTime": "86400",
}


@pytest.fixture()
def mock_client() -> MagicMock:
    c = MagicMock()
    c.device.signal.return_value = SIGNAL_DATA
    c.monitoring.traffic_statistics.return_value = TRAFFIC_DATA
    c.monitoring.status.return_value = STATUS_DATA
    c.net.current_plmn.return_value = PLMN_DATA
    c.device.information.return_value = DEVICE_DATA
    return c


@pytest.fixture()
def collector() -> HuaweiLTECollector:
    return HuaweiLTECollector(Config())


def collect_metrics(col, mock_client) -> dict:
    with (
        patch("huawei_lte_exporter.collector.Connection"),
        patch("huawei_lte_exporter.collector.Client", return_value=mock_client),
    ):
        return {s.name: s.value for m in col.collect() for s in m.samples}
