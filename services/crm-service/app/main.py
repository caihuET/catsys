import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from fastapi import FastAPI
from src.shared.logging import setup_logging
logger = setup_logging("crm-service")
app = FastAPI(title="crm-service", version="0.1")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "crm-service"}

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api.routes import router
app.include_router(router, prefix="/api")
