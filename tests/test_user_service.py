"""用户服务测试 - 覆盖验证码、登录、注册、重置密码全流程"""
import sys, os
_test_root = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.join(_test_root, "..")
sys.path.insert(0, _project_root)

import pytest
from unittest.mock import patch, MagicMock
import importlib.util
import bcrypt


def _load_sms():
    """加载 user-service SMS 模块"""
    svc_path = os.path.join(_project_root, "services", "user-service", "app")
    sys.path.insert(0, svc_path)
    sms_path = os.path.join(svc_path, "service", "sms.py")
    spec = importlib.util.spec_from_file_location("user_sms_test", sms_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_user_routes():
    """加载 user-service API 路由模块"""
    svc_path = os.path.join(_project_root, "services", "user-service", "app")
    sys.path.insert(0, svc_path)
    routes_path = os.path.join(svc_path, "api", "routes.py")
    spec = importlib.util.spec_from_file_location("user_api_routes_test", routes_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===== 验证码模块单元测试 =====

class TestSmsCodeUnit:
    """短信验证码生成、存储、校验单元测试"""

    def setup_method(self):
        self.sms_mod = _load_sms()

    def test_generate_code(self):
        code1 = self.sms_mod._generate_code()
        code2 = self.sms_mod._generate_code()
        assert len(code1) == 6
        assert code1 != code2

    def test_send_sms_mock_mode(self):
        """测试 mock 模式下发送验证码"""
        # 模拟 Redis 连接，避免连接真实 Redis
        redis_patch = patch.object(self.sms_mod, "_get_redis")
        mock_redis = redis_patch.start()
        mock_redis.return_value = MagicMock()
        try:
            result = self.sms_mod.send_sms("13800138000")
            assert result["success"] is True
            assert "mock_" in result["biz_id"]
        finally:
            redis_patch.stop()


# ===== 登录 API 测试 =====

class TestLoginAPI:
    """登录接口测试"""

    def setup_method(self):
        self.mod = _load_user_routes()

    def test_login_success(self):
        """测试成功登录"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.phone = "13800138001"
        mock_user.password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode()
        mock_user.status = "active"
        mock_user.user_type = "merchant_owner"
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            None,
            None,
        ]

        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            req = self.mod.LoginRequest(phone="13800138001", password="testpass123")
            resp = self.mod.login(req)
            assert resp["code"] == 0
            assert resp["data"]["user_id"] == 1
            assert "token" in resp["data"]

    def test_login_wrong_password(self):
        """测试密码错误"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.password_hash = bcrypt.hashpw(b"correctpass", bcrypt.gensalt()).decode()
        mock_user.status = "active"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        from fastapi import HTTPException
        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            req = self.mod.LoginRequest(phone="13800138002", password="wrongpass")
            with pytest.raises(HTTPException) as exc:
                self.mod.login(req)
            assert exc.value.status_code == 401

    def test_login_user_not_found(self):
        """测试用户不存在"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from fastapi import HTTPException
        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            req = self.mod.LoginRequest(phone="99999999999", password="anypass")
            with pytest.raises(HTTPException) as exc:
                self.mod.login(req)
            assert exc.value.status_code == 401

    def test_login_disabled_user(self):
        """测试已禁用用户登录"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
        mock_user.status = "disabled"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        from fastapi import HTTPException
        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            req = self.mod.LoginRequest(phone="13800138003", password="testpass")
            with pytest.raises(HTTPException) as exc:
                self.mod.login(req)
            assert exc.value.status_code == 403


# ===== 发送验证码 API 测试 =====

class TestSendCodeAPI:
    """发送验证码接口测试"""

    def setup_method(self):
        self.mod = _load_user_routes()

    def test_send_code_success(self):
        """测试发送验证码成功"""
        with patch.object(self.mod, "send_sms", return_value={"success": True, "biz_id": "test_biz_001"}):
            req = self.mod.SendCodeRequest(phone="13800138000", type="register")
            resp = self.mod.send_code(req)
            assert resp["code"] == 0
            assert resp["message"] == "验证码已发送"

    def test_send_code_invalid_phone(self):
        """测试手机号格式错误"""
        from fastapi import HTTPException
        req = self.mod.SendCodeRequest(phone="123", type="register")
        with pytest.raises(HTTPException) as exc:
            self.mod.send_code(req)
        assert exc.value.status_code == 400
        assert "手机号格式不正确" in str(exc.value.detail)

    def test_send_code_failure_returns_error(self):
        """测试短信发送失败应返回错误"""
        with patch.object(self.mod, "send_sms", return_value={"success": False, "message": "余额不足"}):
            from fastapi import HTTPException
            req = self.mod.SendCodeRequest(phone="13800138000", type="register")
            with pytest.raises(HTTPException) as exc:
                self.mod.send_code(req)
            assert exc.value.status_code == 502
            assert "余额不足" in str(exc.value.detail)


# ===== 注册 API 测试 =====

class TestRegisterAPI:
    """注册接口测试"""

    def setup_method(self):
        self.mod = _load_user_routes()

    def test_register_success(self):
        """测试成功注册"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            with patch.object(self.mod, "verify_code", return_value=True):
                with patch.object(self.mod, "check_reg_rate_limit", return_value=(True, 0)):
                    with patch.object(self.mod, "increment_reg_count"):
                        req = self.mod.RegisterRequest(
                            phone="13800138010", password="testpass123",
                            business_name="测试猫舍", contact_person="张三",
                            code="123456", client_id="device_test",
                        )
                        resp = self.mod.register(req)
                        assert resp["code"] == 0
                        assert mock_db.add.called
                        assert mock_db.commit.called

    def test_register_wrong_code(self):
        """测试验证码错误"""
        from fastapi import HTTPException
        with patch.object(self.mod, "verify_code", return_value=False):
            req = self.mod.RegisterRequest(
                phone="13800138011", password="testpass",
                business_name="测试猫舍", contact_person="张三", code="000000",
            )
            with pytest.raises(HTTPException) as exc:
                self.mod.register(req)
            assert exc.value.status_code == 400

    def test_register_duplicate_phone(self):
        """测试手机号重复"""
        mock_db = MagicMock()
        existing_user = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user

        from fastapi import HTTPException
        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            with patch.object(self.mod, "verify_code", return_value=True):
                with patch.object(self.mod, "check_reg_rate_limit", return_value=(True, 0)):
                    with patch.object(self.mod, "increment_reg_count"):
                        req = self.mod.RegisterRequest(
                            phone="13800138012", password="newpass",
                            business_name="另一猫舍", contact_person="李四", code="123456",
                        )
                        with pytest.raises(HTTPException) as exc:
                            self.mod.register(req)
                        assert exc.value.status_code == 409

    def test_register_rate_limit(self):
        """测试注册频率限制"""
        from fastapi import HTTPException
        with patch.object(self.mod, "verify_code", return_value=True):
            with patch.object(self.mod, "check_reg_rate_limit", return_value=(False, 3)):
                req = self.mod.RegisterRequest(
                    phone="13800138013", password="testpass",
                    business_name="测试猫舍", contact_person="王五",
                    code="123456", client_id="device_test",
                )
                with pytest.raises(HTTPException) as exc:
                    self.mod.register(req)
                assert exc.value.status_code == 429


# ===== 重置密码 API 测试 =====

class TestResetPasswordAPI:
    """重置密码接口测试"""

    def setup_method(self):
        self.mod = _load_user_routes()

    def test_reset_password_success(self):
        """测试成功重置密码"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.password_hash = bcrypt.hashpw(b"oldpass", bcrypt.gensalt()).decode()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            with patch.object(self.mod, "verify_code", return_value=True):
                req = self.mod.ResetPasswordRequest(
                    phone="13800138020", password="newpass123", code="123456"
                )
                resp = self.mod.reset_password(req)
                assert resp["code"] == 0
                assert mock_db.commit.called

    def test_reset_password_wrong_code(self):
        """测试重置密码验证码错误"""
        from fastapi import HTTPException
        with patch.object(self.mod, "verify_code", return_value=False):
            req = self.mod.ResetPasswordRequest(
                phone="13800138020", password="newpass", code="000000"
            )
            with pytest.raises(HTTPException) as exc:
                self.mod.reset_password(req)
            assert exc.value.status_code == 400

    def test_reset_password_user_not_found(self):
        """测试重置密码用户不存在"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from fastapi import HTTPException
        with patch.object(self.mod, "get_db_sync", return_value=mock_db):
            with patch.object(self.mod, "verify_code", return_value=True):
                req = self.mod.ResetPasswordRequest(
                    phone="99999999999", password="newpass", code="123456"
                )
                with pytest.raises(HTTPException) as exc:
                    self.mod.reset_password(req)
                assert exc.value.status_code == 404
