#!/bin/bash
set -e
PROJECT_ROOT="/opt/catsys"
cd "$PROJECT_ROOT"
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
    echo ">>> Building ${tag} ..."
    docker build -t "${tag}" -f "${df}" .
    BUILT_IMAGES+=("${tag}")
done
echo ">>> Importing images to K3s containerd ..."
for img in "${BUILT_IMAGES[@]}"; do
    echo "  Importing ${img} ..."
    docker save "${img}" | /usr/local/bin/k3s ctr images import -
done
echo "All images built and imported!"
