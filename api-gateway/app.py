import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request, jsonify
from src.shared.config import settings
from src.shared.logging import setup_logging

logger = setup_logging("api-gateway")
app = Flask(__name__)
app.config["SECRET_KEY"] = settings.jwt_secret

SERVICE_MAP = {
    "/api/auth": "http://user-service:5001",
    "/api/users": "http://user-service:5001",
    "/api/employees": "http://user-service:5001",
    "/api/merchants": "http://merchant-service:5002",
    "/api/branches": "http://merchant-service:5002",
    "/api/modules": "http://merchant-service:5002",
    "/api/cats": "http://cat-service:5003",
    "/api/health": "http://cat-service:5003",
    "/api/customers": "http://crm-service:5004",
    "/api/sales": "http://crm-service:5004",
    "/api/contracts": "http://crm-service:5004",
    "/api/followup": "http://crm-service:5004",
    "/api/tasks": "http://crm-service:5004",
    "/api/finance": "http://finance-service:5005",
    "/api/dashboard": "http://dashboard-service:5006",
}

URL_PREFIX = settings.url_prefix

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "api-gateway"})

@app.route("/")
def index():
    return jsonify({"app": settings.app_name, "version": "v0.1"})

@app.route(URL_PREFIX + "/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(subpath):
    import requests
    target_path = "/" + subpath
    target_service = None
    for prefix, url in SERVICE_MAP.items():
        if target_path.startswith(prefix):
            target_service = url + target_path
            break
    if target_path == "/health":
        return jsonify({"status": "ok", "service": "api-gateway"})
    if not target_service:
        return jsonify({"code": 404, "message": "route not found"}), 404
    
    headers = {k: v for k, v in request.headers if k.lower() not in ("host", "content-length")}
    headers["X-Forwarded-Prefix"] = URL_PREFIX
    
    try:
        resp = requests.request(
            method=request.method,
            url=target_service,
            headers=headers,
            params=request.args,
            json=request.get_json(silent=True),
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.ConnectionError:
        return jsonify({"code": 503, "message": "service unavailable"}), 503

if __name__ == "__main__":
    logger.info(f"API Gateway starting on port {settings.api_gateway_port}")
    app.run(host="0.0.0.0", port=settings.api_gateway_port, debug=settings.debug)
URL_PREFIX = settings.url_prefix

SERVICE_MAP = {
    "/api/auth": "http://user-service:5001",
    "/api/users": "http://user-service:5001",
    "/api/employees": "http://user-service:5001",
    "/api/merchants": "http://merchant-service:5002",
    "/api/branches": "http://merchant-service:5002",
    "/api/modules": "http://merchant-service:5002",
    "/api/cats": "http://cat-service:5003",
    "/api/health": "http://cat-service:5003",
    "/api/customers": "http://crm-service:5004",
    "/api/sales": "http://crm-service:5004",
    "/api/contracts": "http://crm-service:5004",
    "/api/followup": "http://crm-service:5004",
    "/api/tasks": "http://crm-service:5004",
    "/api/finance": "http://finance-service:5005",
    "/api/dashboard": "http://dashboard-service:5006",
}

URL_PREFIX = settings.url_prefix

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "api-gateway"})

@app.route(URL_PREFIX + "/health")
def health_with_prefix():
    return jsonify({"status": "ok", "service": "api-gateway"})

@app.route("/")
def index():
    return jsonify({"app": settings.app_name, "version": "v0.1"})

@app.route(URL_PREFIX + "/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])

if __name__ == "__main__":
    logger.info(f"API Gateway starting on port {settings.api_gateway_port}")
    app.run(host="0.0.0.0", port=settings.api_gateway_port, debug=settings.debug)
