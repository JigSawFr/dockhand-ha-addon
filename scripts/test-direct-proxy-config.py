#!/usr/bin/env python3
"""Validate separation between Home Assistant Ingress and direct proxy listeners."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / "dockhand/rootfs/etc/nginx/conf.d/direct.conf"
INGRESS = ROOT / "dockhand/rootfs/etc/nginx/conf.d/ingress.conf"
CONFIG = ROOT / "dockhand/config.yaml"
NGINX = ROOT / "dockhand/rootfs/etc/nginx/nginx.conf"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    direct = DIRECT.read_text(encoding="utf-8") if DIRECT.exists() else ""
    ingress = INGRESS.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")
    nginx = NGINX.read_text(encoding="utf-8")

    require("map_hash_bucket_size 256;" in nginx, "nginx map hash bucket must support maximum-length direct proxy tokens", errors)
    require(DIRECT.exists(), "direct nginx config must exist", errors)
    require(bool(re.search(r"^\s*listen\s+3001;\s*$", direct, re.M)), "direct nginx listener must use port 3001", errors)
    require("absolute_redirect off;" in direct, "direct listener must keep rewritten login redirects relative", errors)
    require("if ($direct_proxy_authorized = 0)" in direct and "return 403;" in direct, "direct listener must reject requests without the configured proxy token", errors)
    require("location = /__direct_health" in direct, "direct listener must expose a loopback-only health endpoint", errors)
    require("proxy_pass         http://127.0.0.1:3000;" in direct, "direct listener must proxy to loopback Dockhand port 3000", errors)
    require("proxy_http_version 1.1;" in direct, "direct listener must use HTTP/1.1", errors)
    require("Upgrade" in direct and "$connection_upgrade" in direct, "direct listener must preserve WebSocket upgrades", errors)
    require("proxy_set_header   X-Dockhand-Proxy-Token \"\";" in direct, "direct listener must not forward its proxy token upstream", errors)
    require("activity/events" in direct and "audit/events" in direct, "direct listener must keep all Dockhand SSE event routes unbuffered", errors)
    require("activity/events" in ingress and "audit/events" in ingress, "Ingress listener must keep all Dockhand SSE event routes unbuffered", errors)
    require("proxy_redirect     ~^https?://[^/]+/login(\\?.*)?$ /login$1;" in direct, "direct listener must rewrite absolute login redirects to the external origin", errors)
    require("proxy_buffering         off;" in direct, "direct stream endpoints must disable response buffering", errors)
    require("proxy_request_buffering off;" in direct, "direct stream endpoints must disable request buffering", errors)

    for forbidden in ["X-Ingress-Path", "sub_filter", "__ha_ingress_shim.js", "allow  172.30.32.2", "deny   all"]:
        require(forbidden not in direct, f"direct listener must not contain {forbidden!r}", errors)

    require(bool(re.search(r"^\s*listen\s+8099;\s*$", ingress, re.M)), "Ingress nginx listener must remain on port 8099", errors)
    require("allow  172.30.32.2;" in ingress and "deny   all;" in ingress, "Ingress listener must remain restricted to the HA gateway", errors)
    require("__ha_ingress_shim.js" in ingress, "Ingress listener must retain the HA shim", errors)

    require(bool(re.search(r"^\s+3001/tcp:\s+null\s*$", config, re.M)), "add-on metadata must declare optional direct port 3001/tcp", errors)
    require(not bool(re.search(r"^\s+3000/tcp:\s+", config, re.M)), "add-on metadata must not publish the loopback-only Dockhand port 3000/tcp", errors)
    require(bool(re.search(r"^\s+direct_proxy_token:\s+[\"']{2}\s*$", config, re.M)), "direct proxy token must be empty by default", errors)
    require(bool(re.search(r"^\s+direct_proxy_token:\s+password\s*$", config, re.M)), "direct proxy token schema must use Home Assistant's masked password type", errors)

    if errors:
        print("direct_proxy_config=fail")
        for error in errors:
            print(f"- {error}")
        return 1

    print("direct_proxy_config=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
