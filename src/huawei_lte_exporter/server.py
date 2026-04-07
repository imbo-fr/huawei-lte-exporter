from __future__ import annotations
import logging
import signal
import sys
from wsgiref.simple_server import make_server

from prometheus_client import REGISTRY, make_wsgi_app

from .collector import HuaweiLTECollector
from .config import Config

log = logging.getLogger(__name__)


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=getattr(logging, level, logging.INFO),
    )


def run(config: Config | None = None) -> None:
    cfg = config or Config()
    _setup_logging(cfg.log_level)
    REGISTRY.register(HuaweiLTECollector(cfg))
    app = make_wsgi_app()
    httpd = make_server(cfg.exporter_host, cfg.exporter_port, app)
    log.info("Listening on %s:%d — /metrics", cfg.exporter_host, cfg.exporter_port)

    def _shutdown(sig, _frame):
        log.info("Signal %s received, shutting down", signal.Signals(sig).name)
        httpd.server_close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
    httpd.serve_forever()
