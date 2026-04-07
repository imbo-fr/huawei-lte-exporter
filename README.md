# huawei-lte-exporter

[![Build](https://github.com/imbo-fr/huawei-lte-exporter/actions/workflows/publish.yml/badge.svg)](https://github.com/imbo-fr/huawei-lte-exporter/actions)
[![Image](https://ghcr.io/imbo-fr/huawei-lte-exporter)](https://ghcr.io/imbo-fr/huawei-lte-exporter)

Prometheus exporter for Huawei LTE routers (B310, B315, B525, B535, B618…) using [huawei-lte-api](https://github.com/Salamek/huawei-lte-api).

## Exposed metrics

| Metric | Type | Description |
|--------|------|-------------|
| `huawei_lte_rsrp_dbm` | Gauge | Reference Signal Received Power |
| `huawei_lte_rsrq_db` | Gauge | Reference Signal Received Quality |
| `huawei_lte_sinr_db` | Gauge | Signal-to-Interference+Noise Ratio |
| `huawei_lte_rssi_dbm` | Gauge | RSSI |
| `huawei_lte_band` | Gauge | Serving LTE band number |
| `huawei_lte_pci` | Gauge | Physical Cell ID |
| `huawei_lte_cell_id` | Gauge | Cell ID |
| `huawei_lte_earfcn` | Gauge | E-ARFCN (channel number) |
| `huawei_lte_txpower_dbm` | Gauge | UE transmit power |
| `huawei_lte_dl_mcs` / `huawei_lte_ul_mcs` | Gauge | DL/UL MCS index |
| `huawei_lte_rx_bytes_total` | Gauge | Total bytes downloaded |
| `huawei_lte_tx_bytes_total` | Gauge | Total bytes uploaded |
| `huawei_lte_rx_rate_bytes_per_second` | Gauge | Current DL throughput |
| `huawei_lte_tx_rate_bytes_per_second` | Gauge | Current UL throughput |
| `huawei_lte_connected` | Gauge | 1 if WAN connected |
| `huawei_lte_signal_bars` | Gauge | Signal bars (0–5) |
| `huawei_lte_roaming` | Gauge | 1 if roaming |
| `huawei_lte_uptime_seconds` | Gauge | Router uptime |
| `huawei_lte_scrape_success` | Gauge | 1 if last scrape succeeded |
| `huawei_lte_signal_info` | Info | mode, lac, cell_id, pci, band labels |
| `huawei_lte_network_info` | Info | operator, mcc_mnc, network_type labels |
| `huawei_lte_device_info` | Info | model, IMEI, firmware labels |

## Quick start

```bash
# Script usage
cp .env.example .env
uv run huawei-lte-exporter

# Docker compose
export ROUTER_PASS=YourAdminPassword
docker compose up -d
```

Metrics: http://localhost:9898/metrics

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ROUTER_URL` | `http://192.168.8.1/` | Router base URL |
| `ROUTER_USER` | `admin` | Router username |
| `ROUTER_PASS` | `admin` | Router password |
| `EXPORTER_PORT` | `9898` | Listening port |
| `EXPORTER_HOST` | `0.0.0.0` | Listening address |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `SCRAPE_TIMEOUT` | `10` | Request timeout (s) |

## Development

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure UV and venv
uv python install 3.12
uv python list 
uv venv --python 3.12

# Install deps
uv sync --extra dev

# Run tests
uv run pytest
```

## Prometheus

Add this scrape configuration to your Prometheus

```yaml
scrape_configs:
  - job_name: "huawei_lte"
    scrape_interval: 30s
    scrape_timeout:  10s
    static_configs:
      - targets: ["huawei-lte-exporter:9898"]
        labels:
          instance: "home_router"
```

## Grafana

Dashboard ID : **XXX** or [grafana/dashboard.json](./grafana/dashboard.json)

## Signal quality reference (for 4G)

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| RSRP | > −80 dBm | −80…−90 | −90…−100 | < −100 dBm |
| RSRQ | > −10 dB | −10…−15 | −15…−20 | < −20 dB |
| SINR | > 20 dB | 13…20 | 0…13 | < 0 dB |

More infos <https://wiki.teltonika-networks.com/view/Mobile_Signal_Strength_Recommendations#4G_and_5G>

## License

MIT
