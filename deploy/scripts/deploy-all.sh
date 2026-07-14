#!/bin/bash
# Cat_Sys CRM - K3s ????
# ??: ./deploy/scripts/deploy-all.sh
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

K3S_DIR="deploy/k3s"
NAMESPACE="cat-sys"

echo "=============================="
echo " Cat_Sys CRM K3s ??"
echo "=============================="

# 1. ????
echo ""
echo "[1/6] Creating namespace ..."
kubectl apply -f "${K3S_DIR}/namespace.yaml"

# 2. ConfigMap
echo "[2/6] Applying ConfigMap ..."
kubectl apply -f "${K3S_DIR}/configmap.yaml"

# 3. Secrets (?? .env ??????)
echo "[3/6] Creating Secrets ..."
MYSQL_PASSWORD="${MYSQL_PASSWORD:-dev_password_123}"
JWT_SECRET="${JWT_SECRET:-dev-jwt-secret-for-development-only}"
kubectl create secret generic cat-sys-secrets -n "${NAMESPACE}" \
  --from-literal=MYSQL_PASSWORD="${MYSQL_PASSWORD}" \
  --from-literal=JWT_SECRET="${JWT_SECRET}" \
  --dry-run=client -o yaml | kubectl apply -f -
echo "  Secrets applied (MYSQL_PASSWORD=${MYSQL_PASSWORD:0:3}***)"

# 4. MySQL
echo "[4/6] Deploying MySQL ..."
kubectl apply -f "${K3S_DIR}/mysql/"
echo "  Waiting for MySQL to be ready ..."
kubectl wait --for=condition=ready pod -l app=mysql -n "${NAMESPACE}" --timeout=180s || echo "  WARNING: MySQL not ready, check with: kubectl get pods -n ${NAMESPACE}"

# 5. Redis
echo "[5/6] Deploying Redis ..."
kubectl apply -f "${K3S_DIR}/redis/"
echo "  Waiting for Redis ..."
kubectl wait --for=condition=ready pod -l app=redis -n "${NAMESPACE}" --timeout=60s || echo "  WARNING: Redis not ready"

# 6. ???
echo "[6/6] Deploying microservices ..."
kubectl apply -f "${K3S_DIR}/services/"

echo ""
echo "=============================="
echo " Deployment complete!"
echo "=============================="
echo ""
echo " Check status:  kubectl get all -n ${NAMESPACE}"
echo " Check pods:    kubectl get pods -n ${NAMESPACE} -w"
echo " Access API:    http://10.0.0.120:30002/cat/health"
echo ""
echo " View logs:"
echo "  kubectl logs -n ${NAMESPACE} -l app=api-gateway"
echo "  kubectl logs -n ${NAMESPACE} -l app=user-service"
echo "  kubectl logs -n ${NAMESPACE} -l app=merchant-service"
