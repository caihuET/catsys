# -*- coding: utf-8 -*-
"""user-service health check test"""
import sys, os, json
import importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestService:
    def setup_method(self):
        app_path = os.path.join(os.path.dirname(__file__), "..", "services", "user-service", "app", "main.py")
        spec = importlib.util.spec_from_file_location("svc_main", app_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.app = mod.app

    def test_health(self):
        from fastapi.testclient import TestClient
        client = TestClient(self.app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
