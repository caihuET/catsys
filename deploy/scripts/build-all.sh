#!/bin/bash
# Cat_Sys CRM - K3s ??????
# ??: ./deploy/scripts/build-all.sh
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=============================="
echo " Cat_Sys CRM ????"
echo "=============================="

SERVICES=(
  "api-gateway:api-gateway/Dockerfile"
  "user-service:services/user-service/Dockerfile"
  "merchant-service:services/merchant-service/Dockerfile"
  "cat-service:services/cat-service/Dockerfile"
  "crm-service:services/crm-service/Dockerfile"
  "finance-service:services/finance-service/Dockerfile"
  "dashboard-service:services/dashboard-service/Dockerfile"
)

BUILT_IMAGES=()

for entry in "${SERVICES[@]}"; do
    svc="${entry%%:*}"
    df="${entry##*:}"
    tag="cat-sys/${svc}:v0.1"
    echo ""
    echo ">>> Building ${tag} ..."
    docker build -t "${tag}" -f "${df}" .
    BUILT_IMAGES+=("${tag}")
done

echo ""
echo "=============================="
echo " Importing images to K3s containerd ..."
echo "=============================="
for img in "${BUILT_IMAGES[@]}"; do
    echo ">>> Importing ${img} ..."
    docker save "${img}" | sudo k3s ctr images import -
done

echo ""
echo " All images built and imported!"
echo ""
echo "Now run: ./deploy/scripts/deploy-all.sh"
