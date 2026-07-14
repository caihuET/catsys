#!/bin/bash
# Cat_Sys ??????
# ??: ./switch-env.sh [dev|prod]

set -e

case "${1:-dev}" in
  dev)
    echo "??????? (10.0.0.120)"
    cp config/development.env .env
    # K3s ConfigMap ??
    kubectl apply -f deploy/k3s/namespace.yaml 2>/dev/null || true
    kubectl create configmap cat-sys-config -n cat-sys \
      --from-literal=DOMAIN=10.0.0.120 \
      --from-literal=SERVER_HOST=10.0.0.120 \
      --from-literal=LOG_LEVEL=DEBUG \
      --dry-run=client -o yaml | kubectl apply -f -
    echo "????????????: kubectl rollout restart deployment -n cat-sys"
    ;;
  prod)
    echo "??????? (67.219.106.150)"
    cp config/production.env .env
    kubectl create configmap cat-sys-config -n cat-sys \
      --from-literal=DOMAIN=xui6.bbbus.top \
      --from-literal=SERVER_HOST=67.219.106.150 \
      --from-literal=LOG_LEVEL=INFO \
      --dry-run=client -o yaml | kubectl apply -f -
    echo "????????????: kubectl rollout restart deployment -n cat-sys"
    ;;
  *)
    echo "??: ./switch-env.sh [dev|prod]"
    exit 1
    ;;
esac
