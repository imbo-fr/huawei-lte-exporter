#!/usr/bin/env python3
"""Run this locally to generate dashboard.json"""

import json

datasource = {"type": "prometheus", "uid": "${datasource}"}
IF = '{instance=~"$instance"}'


def stat(
    pid, title, expr, unit, x, y, w, h, thresholds, decimals=1, color_mode="background"
):
    return {
        "id": pid,
        "type": "stat",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource,
        "targets": [
            {
                "refId": "A",
                "expr": expr,
                "legendFormat": "",
                "instant": True,
                "datasource": datasource,
            }
        ],
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": color_mode,
            "graphMode": "area",
            "justifyMode": "center",
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": decimals,
                "thresholds": {"mode": "absolute", "steps": thresholds},
                "color": {"mode": "thresholds"},
                "mappings": [],
            },
            "overrides": [],
        },
    }


def ts(pid, title, targets, unit, x, y, w, h, thresholds=None, custom=None):
    return {
        "id": pid,
        "type": "timeseries",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource,
        "targets": [
            {
                "refId": chr(65 + i),
                "expr": t["expr"],
                "legendFormat": t.get("legend", ""),
                "datasource": datasource,
            }
            for i, t in enumerate(targets)
        ],
        "options": {
            "tooltip": {"mode": "multi", "sort": "none"},
            "legend": {
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": True,
            },
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "custom": custom
                or {
                    "lineWidth": 2,
                    "fillOpacity": 10,
                    "gradientMode": "none",
                    "showPoints": "never",
                    "spanNulls": True,
                },
                "color": {"mode": "palette-classic"},
                "thresholds": {
                    "mode": "absolute",
                    "steps": thresholds or [{"color": "green", "value": None}],
                },
            },
            "overrides": [],
        },
    }


def gauge(pid, title, expr, unit, x, y, w, h, mn, mx, thresholds):
    return {
        "id": pid,
        "type": "gauge",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource,
        "targets": [
            {
                "refId": "A",
                "expr": expr,
                "legendFormat": "",
                "instant": True,
                "datasource": datasource,
            }
        ],
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "orientation": "auto",
            "showThresholdLabels": False,
            "showThresholdMarkers": True,
        },
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": 0,
                "min": mn,
                "max": mx,
                "thresholds": {"mode": "absolute", "steps": thresholds},
                "color": {"mode": "thresholds"},
                "mappings": [],
            },
            "overrides": [],
        },
    }


def row(pid, title, y):
    return {
        "id": pid,
        "type": "row",
        "title": title,
        "gridPos": {"x": 0, "y": y, "w": 24, "h": 1},
        "collapsed": False,
        "panels": [],
    }


def txt(pid, content, x, y, w, h):
    return {
        "id": pid,
        "type": "text",
        "title": "",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {"mode": "markdown", "content": content},
    }


rsrp = [
    {"color": "dark-red", "value": None},
    {"color": "orange", "value": -115},
    {"color": "yellow", "value": -105},
    {"color": "green", "value": -95},
    {"color": "dark-green", "value": -85},
]
rsrq = [
    {"color": "dark-red", "value": None},
    {"color": "orange", "value": -20},
    {"color": "yellow", "value": -15},
    {"color": "green", "value": -10},
    {"color": "dark-green", "value": -5},
]
sinr = [
    {"color": "dark-red", "value": None},
    {"color": "orange", "value": 0},
    {"color": "yellow", "value": 13},
    {"color": "green", "value": 16},
    {"color": "dark-green", "value": 20},
]
rssi = [
    {"color": "dark-red", "value": None},
    {"color": "orange", "value": -95},
    {"color": "yellow", "value": -85},
    {"color": "green", "value": -75},
    {"color": "dark-green", "value": -65},
]

panels = []

# ── Status row ────────────────────────────────────────────────────────────────
panels.append(row(1, "📡 Connection Status", 0))
p = stat(
    2,
    "Connection",
    f"huawei_lte_connected{IF}",
    "short",
    0,
    1,
    4,
    4,
    [{"color": "red", "value": None}, {"color": "green", "value": 1}],
    0,
)
p["fieldConfig"]["defaults"]["mappings"] = [
    {
        "type": "value",
        "options": {
            "0": {"text": "OFFLINE", "color": "red"},
            "1": {"text": "ONLINE", "color": "green"},
        },
    }
]
panels.append(p)
panels.append(
    stat(
        3,
        "Signal Bars",
        f"huawei_lte_signal_bars{IF}",
        "short",
        4,
        1,
        4,
        4,
        [
            {"color": "dark-red", "value": None},
            {"color": "orange", "value": 1},
            {"color": "yellow", "value": 2},
            {"color": "green", "value": 3},
            {"color": "dark-green", "value": 4},
        ],
        0,
    )
)
p = stat(
    4,
    "Roaming",
    f"huawei_lte_roaming{IF}",
    "short",
    8,
    1,
    4,
    4,
    [{"color": "green", "value": None}, {"color": "orange", "value": 1}],
    0,
)
p["fieldConfig"]["defaults"]["mappings"] = [
    {
        "type": "value",
        "options": {
            "0": {"text": "Home", "color": "green"},
            "1": {"text": "Roaming", "color": "orange"},
        },
    }
]
panels.append(p)
panels.append(
    stat(
        5,
        "Uptime",
        f"huawei_lte_uptime_seconds{IF}",
        "s",
        12,
        1,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
p = stat(
    6,
    "Scrape Health",
    f"huawei_lte_scrape_success{IF}",
    "short",
    16,
    1,
    4,
    4,
    [{"color": "red", "value": None}, {"color": "green", "value": 1}],
    0,
)
p["fieldConfig"]["defaults"]["mappings"] = [
    {
        "type": "value",
        "options": {
            "0": {"text": "FAILED", "color": "red"},
            "1": {"text": "OK", "color": "green"},
        },
    }
]
panels.append(p)
panels.append(
    {
        "id": 7,
        "type": "table",
        "title": "Device Info",
        "gridPos": {"x": 20, "y": 1, "w": 4, "h": 4},
        "datasource": datasource,
        "targets": [
            {
                "refId": "A",
                "expr": f"huawei_lte_device_info{IF}",
                "instant": True,
                "datasource": datasource,
                "format": "table",
            }
        ],
        "options": {"frameIndex": 0, "showHeader": True},
        "transformations": [
            {
                "id": "organize",
                "options": {
                    "excludeByName": {
                        "Time": True,
                        "Value": True,
                        "__name__": True,
                        "instance": True,
                        "job": True,
                    },
                    "renameByName": {
                        "device_name": "Model",
                        "serial_number": "S/N",
                        "hardware_ver": "HW",
                        "software_ver": "FW",
                        "imei": "IMEI",
                    },
                },
            }
        ],
        "fieldConfig": {"defaults": {}, "overrides": []},
    }
)

# ── Signal row ────────────────────────────────────────────────────────────────
panels.append(row(10, "📶 Signal Quality", 5))
panels.append(
    gauge(11, "RSRP", f"huawei_lte_rsrp_dbm{IF}", "dBm", 0, 6, 6, 6, -140, -44, rsrp)
)
panels.append(
    gauge(12, "RSRQ", f"huawei_lte_rsrq_db{IF}", "dB", 6, 6, 6, 6, -20, -3, rsrq)
)
panels.append(
    gauge(13, "SINR", f"huawei_lte_sinr_db{IF}", "dB", 12, 6, 6, 6, -20, 30, sinr)
)
panels.append(
    gauge(14, "RSSI", f"huawei_lte_rssi_dbm{IF}", "dBm", 18, 6, 6, 6, -110, -50, rssi)
)
panels.append(
    ts(
        15,
        "Signal Quality History",
        [
            {"expr": f"huawei_lte_rsrp_dbm{IF}", "legend": "RSRP (dBm)"},
            {"expr": f"huawei_lte_rsrq_db{IF}", "legend": "RSRQ (dB)"},
            {"expr": f"huawei_lte_sinr_db{IF}", "legend": "SINR (dB)"},
            {"expr": f"huawei_lte_rssi_dbm{IF}", "legend": "RSSI (dBm)"},
        ],
        "dB",
        0,
        12,
        24,
        8,
    )
)

# ── Cell info row ─────────────────────────────────────────────────────────────
panels.append(row(20, "🗼 Cell & Radio Info", 20))
panels.append(
    stat(
        21,
        "LTE Band",
        f"huawei_lte_band{IF}",
        "short",
        0,
        21,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
panels.append(
    stat(
        22,
        "PCI",
        f"huawei_lte_pci{IF}",
        "short",
        4,
        21,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
panels.append(
    stat(
        23,
        "Cell ID",
        f"huawei_lte_cell_id{IF}",
        "short",
        8,
        21,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
panels.append(
    stat(
        24,
        "EARFCN",
        f"huawei_lte_earfcn{IF}",
        "short",
        12,
        21,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
panels.append(
    stat(
        25,
        "DL Bandwidth",
        f"huawei_lte_dl_bandwidth{IF}",
        "short",
        16,
        21,
        4,
        4,
        [{"color": "blue", "value": None}],
        0,
        "value",
    )
)
panels.append(
    stat(
        26,
        "TX Power",
        f"huawei_lte_txpower_dbm{IF}",
        "dBm",
        20,
        21,
        4,
        4,
        [
            {"color": "green", "value": None},
            {"color": "orange", "value": 20},
            {"color": "red", "value": 23},
        ],
        1,
        "value",
    )
)
panels.append(
    ts(
        27,
        "MCS (DL / UL)",
        [
            {"expr": f"huawei_lte_dl_mcs{IF}", "legend": "DL MCS"},
            {"expr": f"huawei_lte_ul_mcs{IF}", "legend": "UL MCS"},
        ],
        "short",
        0,
        25,
        12,
        6,
    )
)
panels.append(
    ts(
        28,
        "MIMO Layers",
        [{"expr": f"huawei_lte_dl_mimo_layers{IF}", "legend": "DL MIMO"}],
        "short",
        12,
        25,
        12,
        6,
    )
)
panels.append(
    ts(
        29,
        "Cell Tower Switching",
        [
            {"expr": f"huawei_lte_band{IF}", "legend": "Band"},
            {"expr": f"huawei_lte_pci{IF}", "legend": "PCI"},
        ],
        "short",
        0,
        31,
        24,
        6,
        custom={
            "lineWidth": 2,
            "fillOpacity": 0,
            "gradientMode": "none",
            "showPoints": "always",
            "pointSize": 4,
            "spanNulls": False,
            "drawStyle": "points",
        },
    )
)

# ── Traffic row ───────────────────────────────────────────────────────────────
panels.append(row(30, "📊 Traffic", 37))
panels.append(
    stat(
        31,
        "Current DL Rate",
        f"huawei_lte_rx_rate_bytes_per_second{IF}",
        "Bps",
        0,
        38,
        6,
        4,
        [{"color": "blue", "value": None}],
        1,
        "value",
    )
)
panels.append(
    stat(
        32,
        "Current UL Rate",
        f"huawei_lte_tx_rate_bytes_per_second{IF}",
        "Bps",
        6,
        38,
        6,
        4,
        [{"color": "purple", "value": None}],
        1,
        "value",
    )
)
panels.append(
    stat(
        33,
        "Total Downloaded",
        f"huawei_lte_rx_bytes_total{IF}",
        "bytes",
        12,
        38,
        6,
        4,
        [{"color": "blue", "value": None}],
        2,
        "value",
    )
)
panels.append(
    stat(
        34,
        "Total Uploaded",
        f"huawei_lte_tx_bytes_total{IF}",
        "bytes",
        18,
        38,
        6,
        4,
        [{"color": "purple", "value": None}],
        2,
        "value",
    )
)
panels.append(
    ts(
        35,
        "Throughput (DL / UL)",
        [
            {"expr": f"huawei_lte_rx_rate_bytes_per_second{IF}", "legend": "Download"},
            {"expr": f"huawei_lte_tx_rate_bytes_per_second{IF}", "legend": "Upload"},
        ],
        "Bps",
        0,
        42,
        24,
        8,
        custom={
            "lineWidth": 2,
            "fillOpacity": 20,
            "gradientMode": "opacity",
            "showPoints": "never",
            "spanNulls": True,
        },
    )
)
panels.append(
    ts(
        36,
        "Session Bytes",
        [
            {"expr": f"huawei_lte_session_rx_bytes{IF}", "legend": "Session DL"},
            {"expr": f"huawei_lte_session_tx_bytes{IF}", "legend": "Session UL"},
        ],
        "bytes",
        0,
        50,
        24,
        6,
    )
)

# ── Diagnostics row ───────────────────────────────────────────────────────────
panels.append(row(40, "🔧 Diagnostics", 56))
panels.append(
    ts(
        41,
        "Scrape Success",
        [{"expr": f"huawei_lte_scrape_success{IF}", "legend": "OK"}],
        "short",
        0,
        57,
        8,
        5,
        thresholds=[{"color": "red", "value": None}, {"color": "green", "value": 1}],
    )
)
panels.append(
    ts(
        42,
        "Uptime",
        [{"expr": f"huawei_lte_uptime_seconds{IF}", "legend": "Uptime"}],
        "s",
        8,
        57,
        8,
        5,
    )
)
panels.append(
    ts(
        43,
        "Signal Bars",
        [{"expr": f"huawei_lte_signal_bars{IF}", "legend": "Bars"}],
        "short",
        16,
        57,
        8,
        5,
    )
)

panels.append(
    txt(
        50,
        """## LTE Signal Quality Reference

| Metric | Excellent | Good | Fair | Weak | Poor |
|--------|-----------|------|------|------|------|
| **RSRP** | > -85 dBm | -85…-95 | -95…-105 | -105…-115 | < -115 dBm |
| **RSRQ** | > -5 dB | -5…-10 | -10…-15 | -15…-20 | < -20 dB |
| **SINR** | > 20 dB | 16…20 | 13…16 | 3…13 | < 3 dB |
| **RSSI** | > -65 dBm | -65…-75 | -75…-85 | -85…-95 | < -95 dBm |""",
        0,
        62,
        24,
        7,
    )
)

dashboard = {
    "__inputs": [
        {
            "name": "DS_PROMETHEUS",
            "label": "Prometheus",
            "type": "datasource",
            "pluginId": "prometheus",
            "pluginName": "Prometheus",
        }
    ],
    "__requires": [
        {"type": "grafana", "id": "grafana", "name": "Grafana", "version": "9.0.0"},
        {
            "type": "datasource",
            "id": "prometheus",
            "name": "Prometheus",
            "version": "1.0.0",
        },
        {"type": "panel", "id": "stat", "name": "Stat", "version": ""},
        {"type": "panel", "id": "timeseries", "name": "Time series", "version": ""},
        {"type": "panel", "id": "gauge", "name": "Gauge", "version": ""},
        {"type": "panel", "id": "table", "name": "Table", "version": ""},
        {"type": "panel", "id": "text", "name": "Text", "version": ""},
    ],
    "annotations": {
        "list": [
            {
                "builtIn": 1,
                "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                "enable": True,
                "hide": True,
                "iconColor": "rgba(0,211,255,1)",
                "name": "Annotations & Alerts",
                "type": "dashboard",
            }
        ]
    },
    "description": "Huawei LTE router monitoring — signal, traffic, cell info, uptime.",
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 1,
    "id": None,
    "links": [],
    "liveNow": False,
    "panels": panels,
    "refresh": "30s",
    "schemaVersion": 38,
    "style": "dark",
    "tags": ["lte", "4g", "huawei", "networking"],
    "templating": {
        "list": [
            {
                "current": {},
                "hide": 0,
                "includeAll": False,
                "multi": False,
                "name": "datasource",
                "options": [],
                "query": "prometheus",
                "refresh": 1,
                "regex": "",
                "type": "datasource",
                "label": "Datasource",
            },
            {
                "current": {},
                "datasource": datasource,
                "definition": "label_values(huawei_lte_scrape_success, instance)",
                "hide": 0,
                "includeAll": False,
                "multi": False,
                "name": "instance",
                "options": [],
                "query": {
                    "query": "label_values(huawei_lte_scrape_success, instance)",
                    "refId": "StandardVariableQuery",
                },
                "refresh": 2,
                "regex": "",
                "sort": 1,
                "type": "query",
                "label": "Instance",
            },
        ]
    },
    "time": {"from": "now-6h", "to": "now"},
    "timepicker": {},
    "timezone": "browser",
    "title": "Huawei LTE Router",
    "uid": "huawei-lte-exporter",
    "version": 1,
    "weekStart": "",
}

with open("dashboard.json", "w") as f:
    json.dump(dashboard, f, indent=2)

print(f"Generated dashboard.json — {len(panels)} panels")
