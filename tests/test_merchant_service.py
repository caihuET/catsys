"""商家服务健康检查测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import importlib.util
import json


def _load_merchant_service():
    """加载商家服务模块"""
    app_path = os.path.join(os.path.dirname(__file__), "..", "services", "merchant-service", "app", "main.py")
    spec = importlib.util.spec_from_file_location("merchant_svc_test", app_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestMerchantService:
    def setup_method(self):
        self.mod = _load_merchant_service()
        from fastapi.testclient import TestClient
        self.client = TestClient(self.mod.app)

    def test_health(self):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_routes_loaded(self):
        """验证路由已注册"""
        routes = [r.path for r in self.mod.app.routes]
        assert "/health" in routes
