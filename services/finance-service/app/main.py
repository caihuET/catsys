import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from fastapi import FastAPI
from src.shared.logging import setup_logging
logger = setup_logging("finance-service")
app = FastAPI(title="finance-service", version="0.1")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "finance-service"}
