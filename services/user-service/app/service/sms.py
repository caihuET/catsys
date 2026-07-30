# -*- coding: utf-8 -*-
"""短信验证码服务 - 阿里云号码认证服务Dypnsapi"""
import json
import logging
from typing import Optional, Tuple

import redis
from src.shared.config import settings

logger = logging.getLogger("user-service.sms")


def _get_redis() -> redis.Redis:
    """获取 Redis 连接"""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password or None,
        db=0,
        decode_responses=True,
    )


def store_code(phone: str, code: str) -> None:
    """将验证码存入 Redis，带过期时间"""
    r = _get_redis()
    key = f"sms:code:{phone}"
    r.setex(key, settings.sms_code_expire_seconds, code)
    logger.info("验证码已存入 Redis: phone=%s, expire=%ss", phone, settings.sms_code_expire_seconds)


def verify_code(phone: str, code: str) -> bool:
    """校验验证码，校验后立即删除（一次性）"""
    r = _get_redis()
    key = f"sms:code:{phone}"
    stored = r.get(key)
    if stored is None:
        return False
    if stored == code:
        r.delete(key)
        return True
    return False


def _generate_code() -> str:
    """生成 6 位随机数字验证码"""
    import random
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def send_sms(phone: str) -> dict:
    """通过阿里云 Dypnsapi 发送短信验证码

    验证码由本地生成并存入 Redis 用于后续校验。
    阿里云 SDK 不可用时自动降级为本地 mock 模式。
    """
    try:
        from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
        from alibabacloud_tea_util import models as util_models

        code = _generate_code()

        config = open_api_models.Config(
            access_key_id=settings.aliyun_sms_access_key_id,
            access_key_secret=settings.aliyun_sms_access_key_secret,
        )
        config.endpoint = "dypnsapi.aliyuncs.com"
        client = DypnsapiClient(config)

        req = dypnsapi_models.SendSmsVerifyCodeRequest(
            sign_name=settings.aliyun_sms_sign_name,
            template_code=settings.aliyun_sms_template_code,
            phone_number=phone,
            template_param=json.dumps({"code": code, "min": "5"}),
            code_type=2,
        )
        runtime = util_models.RuntimeOptions()
        resp = client.send_sms_verify_code_with_options(req, runtime)
        body = resp.body

        if body.code == "OK":
            store_code(phone, code)
            logger.info("短信发送成功: phone=%s, biz_id=%s", phone, body.model.biz_id)
            return {"success": True, "biz_id": body.model.biz_id}
        else:
            logger.error("短信发送失败: phone=%s, code=%s, message=%s", phone, body.code, body.message)
            return {"success": False, "code": body.code, "message": body.message}
    except ImportError as e:
        logger.warning("alibabacloud SDK 未安装(%s)，使用本地生成模式: phone=%s", e, phone)
        code = _generate_code()
        store_code(phone, code)
        logger.info("模拟发送短信: phone=%s, code=%s", phone, code)
        return {"success": True, "biz_id": "mock_" + code}
    except Exception as e:
        logger.exception("短信发送异常: phone=%s", phone)
        return {"success": False, "message": str(e)}


def check_reg_rate_limit(ip: str, client_id: str) -> Tuple[bool, int]:
    """检查注册频率限制（同一IP+设备 24小时内最多 reg_limit_count 次）
    返回 (是否允许, 已注册次数)
    """
    r = _get_redis()
    key = f"reg:limit:{ip}:{client_id}"
    count = r.get(key)
    current = int(count) if count else 0
    limit = settings.reg_limit_count
    if current >= limit:
        logger.warning("注册频率限制触发: ip=%s, client_id=%s, count=%d", ip, client_id, current)
        return False, current
    return True, current


def increment_reg_count(ip: str, client_id: str) -> None:
    """注册成功后增加计数"""
    r = _get_redis()
    key = f"reg:limit:{ip}:{client_id}"
    hours = settings.reg_limit_hours
    r.incr(key)
    r.expire(key, hours * 3600)
