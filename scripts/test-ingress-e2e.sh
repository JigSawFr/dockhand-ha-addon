#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-dockhand-ha-addon:smoke}
NETWORK=${NETWORK:-dockhand-ingress-e2e}
SUBNET=${SUBNET:-172.30.32.0/24}
ADDON_IP=${ADDON_IP:-172.30.32.10}
GATEWAY_IP=${GATEWAY_IP:-172.30.32.2}
BAD_IP=${BAD_IP:-172.30.32.3}
INGRESS_PATH=${INGRESS_PATH:-/api/hassio_ingress/e2e-token}
ADDON_NAME=${ADDON_NAME:-dockhand-ingress-e2e-addon}

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build -t "$IMAGE" ./dockhand
fi

cleanup() {
    docker rm -f "$ADDON_NAME" >/dev/null 2>&1 || true
    docker network rm "$NETWORK" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker network create --subnet "$SUBNET" "$NETWORK" >/dev/null

start_cmd='set -euo pipefail
mkdir -p /data/db /tmp/nginx/client_temp /tmp/nginx/proxy_temp /tmp/nginx/fastcgi_temp /tmp/nginx/uwsgi_temp /tmp/nginx/scgi_temp
cd /app
DATA_DIR=/data PORT=3000 HOST=127.0.0.1 NODE_ENV=production node /app/server.js >/tmp/dockhand.log 2>&1 &
for i in $(seq 1 60); do
    if curl -fsS --max-time 2 http://127.0.0.1:3000/ >/tmp/dockhand-root.html 2>/tmp/dockhand-curl.err; then
        break
    fi
    sleep 1
done
curl -fsS --max-time 2 http://127.0.0.1:3000/ >/dev/null
exec nginx -g "daemon off;"'

docker run -d \
    --name "$ADDON_NAME" \
    --network "$NETWORK" \
    --ip "$ADDON_IP" \
    --entrypoint /bin/bash \
    "$IMAGE" \
    -lc "$start_cmd" >/dev/null

for _ in $(seq 1 60); do
    if docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" -lc "curl -fsS --max-time 2 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/ >/dev/null"; then
        break
    fi
    sleep 1
done

html=$(mktemp)
shim=$(mktemp)
trap 'rm -f "$html" "$shim"; cleanup' EXIT

docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/" > "$html"

grep -F "<base href=\"$INGRESS_PATH/\">" "$html" >/dev/null
grep -F '__ha_ingress_shim.js' "$html" >/dev/null

docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/__ha_ingress_shim.js" > "$shim"
grep -F 'function fix(url)' "$shim" >/dev/null

bad_status=$(docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -sS --max-time 5 -o /dev/null -w '%{http_code}' -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/" || true)
[ "$bad_status" = "403" ] || { echo "expected non-ingress gateway to receive 403, got $bad_status"; docker logs "$ADDON_NAME"; exit 1; }

echo 'ingress_e2e=ok'
