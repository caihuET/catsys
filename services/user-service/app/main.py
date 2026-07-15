import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from fastapi import FastAPI
from src.shared.config import settings
from src.shared.database import init_db
from src.shared.logging import setup_logging

logger = setup_logging("user-service")
app = FastAPI(title="user-service", version="0.1")

@app.on_event("startup")
async def startup():
    init_db()
    logger.info("user-service started")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "user-service"}

# 添加 app 目录到 sys.path，使 api.routes 可被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api.routes import router
app.include_router(router, prefix="/api")
