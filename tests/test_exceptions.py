# -*- coding: utf-8 -*-
"""Exception unit tests"""
from src.shared.exceptions import (
    AppException, NotFoundError, UnauthorizedError,
    ForbiddenError, BusinessError,
)

class TestExceptions:
    def test_app_exception(self):
        e = AppException("test error", 400)
        assert str(e) == "test error"
        assert e.code == 400

    def test_not_found(self):
        e = NotFoundError()
        assert e.code == 404
        assert len(e.message) > 0

    def test_unauthorized(self):
        e = UnauthorizedError()
        assert e.code == 401

    def test_forbidden(self):
        e = ForbiddenError()
        assert e.code == 403

    def test_business_error(self):
        e = BusinessError()
        assert e.code == 422
