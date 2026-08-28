#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-dockhand-ha-addon:smoke}
NETWORK=${NETWORK:-dockhand-ingress-e2e}
SUBNET=${SUBNET:-172.30.32.0/24}
ADDON_IP=${ADDON_IP:-172.30.32.10}
GATEWAY_IP=${GATEWAY_IP:-172.30.32.2}
BAD_IP=${BAD_IP:-172.30.32.3}
DIRECT_PROXY_TOKEN=${DIRECT_PROXY_TOKEN:-E2EProxyToken_0123456789_ABCDEFGHIJK}
E2E_CREDENTIAL=${E2E_CREDENTIAL:-E2E-Credential-Only-For-Isolated-CI}
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
DOCKHAND_SEED_REQUIRE_SOCKET=false bash /usr/bin/dockhand-seed-ha-environment
bash /etc/cont-init.d/04-direct-proxy-auth.sh
exec nginx -g "daemon off;"'

docker run -d \
    --name "$ADDON_NAME" \
    --network "$NETWORK" \
    --ip "$ADDON_IP" \
    --env "DOCKHAND_TEST_DIRECT_PROXY_TOKEN=$DIRECT_PROXY_TOKEN" \
    --entrypoint /bin/bash \
    "$IMAGE" \
    -lc "$start_cmd" >/dev/null

ready=false
for _ in $(seq 1 60); do
    if docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" -lc "curl -fsS --max-time 2 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/ >/dev/null"; then
        ready=true
        break
    fi
    sleep 1
done
if [ "$ready" != "true" ]; then
    echo 'add-on did not become ready on ingress port'
    docker logs "$ADDON_NAME" || true
    exit 1
fi

html=$(mktemp)
shim=$(mktemp)
environments=$(mktemp)
direct_html=$(mktemp)
direct_headers=$(mktemp)
trap 'rm -f "$html" "$shim" "$environments" "$direct_html" "$direct_headers"; cleanup' EXIT

docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/" > "$html"

grep -F "<base href=\"$INGRESS_PATH/\">" "$html" >/dev/null
grep -F '__ha_ingress_shim.js' "$html" >/dev/null

docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/__ha_ingress_shim.js" > "$shim"
grep -F 'function fix(url)' "$shim" >/dev/null

docker run --rm --network "$NETWORK" --ip "$GATEWAY_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/api/environments" > "$environments"
grep -F '"name":"Home Assistant"' "$environments" >/dev/null
grep -F '"socketPath":"/var/run/docker.sock"' "$environments" >/dev/null
grep -F '"labels":["ha"]' "$environments" >/dev/null

# Enable Dockhand authentication so redirect rewriting is exercised rather than
# accepting an empty Location header from the unauthenticated bootstrap state.
docker exec --env "DOCKHAND_E2E_CREDENTIAL=$E2E_CREDENTIAL" "$ADDON_NAME" bash -lc '
    user_payload=$(printf '\''{"username":"e2e-admin","%s":"%s","displayName":"E2E"}'\'' password "$DOCKHAND_E2E_CREDENTIAL")
    curl -fsS --max-time 15 -X POST -H '\''Content-Type: application/json'\'' -d "$user_payload" http://127.0.0.1:3000/api/users >/dev/null
    curl -fsS --max-time 10 -X PUT -H '\''Content-Type: application/json'\'' -d '\''{"authEnabled":true}'\'' http://127.0.0.1:3000/api/auth/settings >/dev/null
'

# A sibling add-on must not reach Dockhand's loopback-only app port.
loopback_status=$(docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -sS --max-time 3 -o /dev/null -w '%{http_code}' http://$ADDON_IP:3000/" || true)
[ "$loopback_status" = "000" ] || { echo "expected direct app port 3000 to be unreachable, got $loopback_status"; docker logs "$ADDON_NAME"; exit 1; }

# The dedicated proxy endpoint denies network clients without its shared token.
unauthorized_status=$(docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -sS --max-time 5 -o /dev/null -w '%{http_code}' http://$ADDON_IP:3001/" || true)
[ "$unauthorized_status" = "403" ] || { echo "expected direct proxy without token to receive 403, got $unauthorized_status"; docker logs "$ADDON_NAME"; exit 1; }

# nginx map string keys are case-insensitive; the generated regex must not be.
case_variant=$(printf '%s' "$DIRECT_PROXY_TOKEN" | tr '[:lower:]' '[:upper:]')
[ "$case_variant" != "$DIRECT_PROXY_TOKEN" ] || { echo 'E2E credential fixture must contain lowercase characters'; exit 1; }
case_variant_status=$(docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -sS --max-time 5 -o /dev/null -w '%{http_code}' -H 'X-Dockhand-Proxy-Token: $case_variant' http://$ADDON_IP:3001/" || true)
[ "$case_variant_status" = "403" ] || { echo "expected case-mutated direct proxy credential to receive 403, got $case_variant_status"; docker logs "$ADDON_NAME"; exit 1; }

# A trusted sibling reverse proxy can reach 3001 with the configured token,
# without receiving HA Ingress HTML rewriting.
docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -H 'X-Dockhand-Proxy-Token: $DIRECT_PROXY_TOKEN' -H 'Host: dockhand.example.test' -H 'X-Forwarded-Host: dockhand.example.test' -H 'X-Forwarded-Proto: https' http://$ADDON_IP:3001/" > "$direct_html"
docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -fsS --max-time 5 -D - -o /dev/null -H 'X-Dockhand-Proxy-Token: $DIRECT_PROXY_TOKEN' -H 'Host: dockhand.example.test' -H 'X-Forwarded-Host: dockhand.example.test' -H 'X-Forwarded-Proto: https' http://$ADDON_IP:3001/" > "$direct_headers"
if grep -F '__ha_ingress_shim.js' "$direct_html" >/dev/null; then
    echo 'direct endpoint must not inject the HA Ingress shim'
    docker logs "$ADDON_NAME"
    exit 1
fi
if grep -F "<base href=\"$INGRESS_PATH/\">" "$direct_html" >/dev/null; then
    echo 'direct endpoint must not inject the HA Ingress base path'
    docker logs "$ADDON_NAME"
    exit 1
fi
direct_status=''
direct_location=''
while IFS= read -r header; do
    header=${header%$'\r'}
    case "$header" in
        HTTP/*)
            status_and_reason=${header#* }
            direct_status=${status_and_reason%% *}
            ;;
        [Ll][Oo][Cc][Aa][Tt][Ii][Oo][Nn]:*) direct_location=${header#*: } ;;
    esac
done < "$direct_headers"
[ "$direct_status" = "307" ] || { echo "expected authenticated direct endpoint to return 307, got $direct_status"; docker logs "$ADDON_NAME"; exit 1; }
case "$direct_location" in
    /login*) ;;
    *) echo "direct endpoint did not return a relative login redirect: $direct_location"; docker logs "$ADDON_NAME"; exit 1 ;;
esac

bad_status=$(docker run --rm --network "$NETWORK" --ip "$BAD_IP" --entrypoint /bin/bash "$IMAGE" \
    -lc "curl -sS --max-time 5 -o /dev/null -w '%{http_code}' -H 'X-Ingress-Path: $INGRESS_PATH' http://$ADDON_IP:8099/" || true)
[ "$bad_status" = "403" ] || { echo "expected non-ingress gateway to receive 403, got $bad_status"; docker logs "$ADDON_NAME"; exit 1; }

echo 'ingress_e2e=ok'
