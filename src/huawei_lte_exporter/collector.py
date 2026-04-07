from __future__ import annotations
import logging
from typing import Iterator

from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, Metric
from prometheus_client.registry import Collector

from .config import Config
from .utils import connection_status_to_int, to_float

log = logging.getLogger(__name__)


class HuaweiLTECollector(Collector):
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()

    def collect(self) -> Iterator[Metric]:
        scrape_ok = GaugeMetricFamily(
            "huawei_lte_scrape_success",
            "1 if the last scrape succeeded, 0 otherwise",
        )
        try:
            with Connection(self.config.router_url_with_auth) as conn:
                client = Client(conn)
                yield from self._signal(client)
                yield from self._traffic(client)
                yield from self._status(client)
                yield from self._device(client)
            scrape_ok.add_metric([], 1.0)
        except Exception:
            log.exception("Scrape failed")
            scrape_ok.add_metric([], 0.0)
        yield scrape_ok

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _g(name: str, doc: str, raw: object) -> GaugeMetricFamily:
        g = GaugeMetricFamily(name, doc)
        g.add_metric([], to_float(raw))
        return g

    # ── signal ───────────────────────────────────────────────────────────────

    def _signal(self, client: Client) -> Iterator[Metric]:
        d = client.device.signal()
        for name, doc, key in [
            ("huawei_lte_rssi_dbm", "RSSI (dBm)", "rssi"),
            ("huawei_lte_rsrp_dbm", "RSRP (dBm)", "rsrp"),
            ("huawei_lte_rsrq_db", "RSRQ (dB)", "rsrq"),
            ("huawei_lte_sinr_db", "SINR (dB)", "sinr"),
            ("huawei_lte_rscp_dbm", "RSCP (dBm) — WCDMA", "rscp"),
            ("huawei_lte_ecio_db", "Ec/Io (dB) — WCDMA", "ecio"),
            ("huawei_lte_band", "Serving LTE band number", "band"),
            ("huawei_lte_cell_id", "Serving cell ID", "cell_id"),
            ("huawei_lte_pci", "Physical Cell ID", "pci"),
            ("huawei_lte_earfcn", "E-ARFCN", "earfcn"),
            ("huawei_lte_dl_bandwidth", "Downlink bandwidth (MHz)", "dlbandwidth"),
            ("huawei_lte_ul_bandwidth", "Uplink bandwidth (MHz)", "ulbandwidth"),
            ("huawei_lte_txpower_dbm", "UE TX power (dBm)", "txpower"),
            ("huawei_lte_dl_mcs", "DL MCS index", "dlmcs"),
            ("huawei_lte_ul_mcs", "UL MCS index", "ulmcs"),
            ("huawei_lte_dl_mimo_layers", "DL MIMO spatial streams", "nrdlmimolayers"),
        ]:
            yield self._g(name, doc, d.get(key))

        info = InfoMetricFamily("huawei_lte_signal", "Signal label info")
        info.add_metric(
            [],
            {
                "mode": str(d.get("mode", "")),
                "lac": str(d.get("lac", "")),
                "cell_id": str(d.get("cell_id", "")),
                "pci": str(d.get("pci", "")),
                "band": str(d.get("band", "")),
            },
        )
        yield info

    # ── traffic ──────────────────────────────────────────────────────────────

    def _traffic(self, client: Client) -> Iterator[Metric]:
        d = client.monitoring.traffic_statistics()
        for name, doc, key in [
            ("huawei_lte_rx_bytes_total", "Total bytes RX", "TotalDownload"),
            ("huawei_lte_tx_bytes_total", "Total bytes TX", "TotalUpload"),
            (
                "huawei_lte_rx_rate_bytes_per_second",
                "Current DL rate (B/s)",
                "CurrentDownloadRate",
            ),
            (
                "huawei_lte_tx_rate_bytes_per_second",
                "Current UL rate (B/s)",
                "CurrentUploadRate",
            ),
            ("huawei_lte_session_rx_bytes", "Session DL bytes", "CurrentDownload"),
            ("huawei_lte_session_tx_bytes", "Session UL bytes", "CurrentUpload"),
        ]:
            yield self._g(name, doc, d.get(key))

    # ── status ───────────────────────────────────────────────────────────────

    def _status(self, client: Client) -> Iterator[Metric]:
        d = client.monitoring.status()
        yield self._g(
            "huawei_lte_signal_bars", "Signal bars (0-5)", d.get("SignalIcon")
        )
        yield self._g("huawei_lte_roaming", "1 if roaming", d.get("RoamingStatus"))

        c = GaugeMetricFamily("huawei_lte_connected", "1 if WAN connected")
        c.add_metric([], connection_status_to_int(d.get("ConnectionStatus")))
        yield c

        try:
            plmn = client.net.current_plmn()
        except Exception:
            plmn = {}

        ni = InfoMetricFamily("huawei_lte_network", "Network operator info")
        ni.add_metric(
            [],
            {
                "operator": str(plmn.get("FullName", "")),
                "short_name": str(plmn.get("ShortName", "")),
                "mcc_mnc": str(plmn.get("Numeric", "")),
                "network_type": str(d.get("CurrentNetworkType", "")),
            },
        )
        yield ni

    # ── device ───────────────────────────────────────────────────────────────

    def _device(self, client: Client) -> Iterator[Metric]:
        d = client.device.information()
        yield self._g("huawei_lte_uptime_seconds", "Router uptime (s)", d.get("UpTime"))

        di = InfoMetricFamily("huawei_lte_device", "Device static info")
        di.add_metric(
            [],
            {
                "device_name": str(d.get("DeviceName", "")),
                "serial_number": str(d.get("SerialNumber", "")),
                "imei": str(d.get("Imei", "")),
                "hardware_ver": str(d.get("HardwareVersion", "")),
                "software_ver": str(d.get("SoftwareVersion", "")),
            },
        )
        yield di
