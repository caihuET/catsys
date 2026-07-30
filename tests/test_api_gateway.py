"""API Gateway 接口测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import importlib.util
import pytest


def _load_gateway():
    """加载 API Gateway 模块"""
    gw_path = os.path.join(os.path.dirname(__file__), "..", "api-gateway", "app.py")
    spec = importlib.util.spec_from_file_location("gateway_app_test", gw_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestApiGateway:
    """API Gateway 健康检查和路由测试"""

    def setup_method(self):
        self.mod = _load_gateway()
        self.app = self.mod.app.test_client()

    def test_health_endpoint(self):
        """测试健康检查端点"""
        resp = self.app.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"
        assert data["service"] == "api-gateway"

    def test_index_endpoint(self):
        """测试根路由"""
        resp = self.app.get("/")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "app" in data
        assert "version" in data

    def test_health_with_prefix(self):
        """测试带前缀的健康检查路由"""
        prefix = self.mod.URL_PREFIX
        if prefix:
            resp = self.app.get(prefix + "/health")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["status"] == "ok"

    def test_unknown_route_returns_404(self):
        """测试未知路由返回 404 或 503"""
        prefix = self.mod.URL_PREFIX
        resp = self.app.get(prefix + "/api/nonexistent")
        assert resp.status_code in (404, 503)
        if resp.status_code == 404:
            data = json.loads(resp.data)
            assert data["code"] == 404
