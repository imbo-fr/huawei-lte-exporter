from __future__ import annotations
from unittest.mock import patch
import pytest
from huawei_lte_exporter.collector import HuaweiLTECollector
from huawei_lte_exporter.config import Config
from conftest import collect_metrics


def test_rsrp(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_rsrp_dbm"] == -95.0


def test_rsrq(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_rsrq_db"] == -12.0


def test_sinr(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_sinr_db"] == 15.0


def test_rssi(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_rssi_dbm"] == -75.0


def test_null_field_defaults_to_zero(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_rscp_dbm"] == 0.0


def test_rx_bytes_total(collector, mock_client):
    assert (
        collect_metrics(collector, mock_client)["huawei_lte_rx_bytes_total"]
        == 10_737_418_240.0
    )


def test_tx_rate(collector, mock_client):
    assert (
        collect_metrics(collector, mock_client)["huawei_lte_tx_rate_bytes_per_second"]
        == 131_072.0
    )


def test_connected_when_901(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_connected"] == 1.0


def test_disconnected_when_902(collector, mock_client):
    mock_client.monitoring.status.return_value = {
        "SignalIcon": "2",
        "ConnectionStatus": "902",
        "RoamingStatus": "0",
        "CurrentNetworkType": "19",
    }
    assert collect_metrics(collector, mock_client)["huawei_lte_connected"] == 0.0


def test_signal_bars(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_signal_bars"] == 4.0


def test_uptime(collector, mock_client):
    assert (
        collect_metrics(collector, mock_client)["huawei_lte_uptime_seconds"] == 86_400.0
    )


def test_scrape_success_metric(collector, mock_client):
    assert collect_metrics(collector, mock_client)["huawei_lte_scrape_success"] == 1.0


def test_scrape_failure_metric(collector):
    with patch(
        "huawei_lte_exporter.collector.Connection", side_effect=Exception("refused")
    ):
        metrics = {s.name: s.value for m in collector.collect() for s in m.samples}
    assert metrics["huawei_lte_scrape_success"] == 0.0


def test_plmn_failure_does_not_crash(collector, mock_client):
    mock_client.net.current_plmn.side_effect = Exception("not supported")
    m = collect_metrics(collector, mock_client)
    assert "huawei_lte_connected" in m
    assert m["huawei_lte_scrape_success"] == 1.0
