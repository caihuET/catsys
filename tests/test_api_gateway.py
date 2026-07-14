# -*- coding: utf-8 -*-
"""API Gateway interface test"""
import sys, os, json
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestApiGateway:
    def setup_method(self):
        gw_path = os.path.join(os.path.dirname(__file__), "..", "api-gateway", "app.py")
        spec = importlib.util.spec_from_file_location("gateway_app", gw_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.app = mod.app.test_client()

    def test_health_endpoint(self):
        resp = self.app.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"

    def test_index_endpoint(self):
        resp = self.app.get("/")
        assert resp.status_code in (200, 302, 404)

    def test_unknown_route(self):
        resp = self.app.get("/api/nonexistent")
        assert resp.status_code in (404, 500, 503)
