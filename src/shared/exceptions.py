class AppException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class NotFoundError(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)

class UnauthorizedError(AppException):
    def __init__(self, message: str = "未授权"):
        super().__init__(message, 401)

class ForbiddenError(AppException):
    def __init__(self, message: str = "没有权限"):
        super().__init__(message, 403)

class BusinessError(AppException):
    def __init__(self, message: str = "业务错误"):
        super().__init__(message, 422)
