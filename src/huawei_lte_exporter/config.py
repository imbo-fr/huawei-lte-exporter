from __future__ import annotations
import os


class Config:
    router_url: str = os.environ.get("ROUTER_URL", "http://192.168.8.1/")
    router_user: str = os.environ.get("ROUTER_USER", "admin")
    router_pass: str = os.environ.get("ROUTER_PASS", "admin")
    exporter_host: str = os.environ.get("EXPORTER_HOST", "0.0.0.0")
    exporter_port: int = int(os.environ.get("EXPORTER_PORT", "9898"))
    log_level: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    scrape_timeout: int = int(os.environ.get("SCRAPE_TIMEOUT", "10"))

    @property
    def router_url_with_auth(self) -> str:
        url = self.router_url.rstrip("/")
        scheme, rest = url.split("://", 1)
        return f"{scheme}://{self.router_user}:{self.router_pass}@{rest}/"
