from src.shared.config import settings
from src.shared.exceptions import AppException, NotFoundError, UnauthorizedError, ForbiddenError, BusinessError
from src.shared.logging import setup_logging

# Database - lazy import to avoid chain import on simple tests
def get_db():
    from src.shared.database import get_db_sync
    return get_db_sync()

def init_db():
    from src.shared.database import init_db as _init
    _init()
