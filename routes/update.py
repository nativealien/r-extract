import os
import json
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

router = APIRouter(prefix="/update", tags=["update"])

@router.get("")
async def check_auth(x_api_key: str = Header(alias="X-API-Key")):

    key = os.getenv("API_KEY")

    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Load test_tickers.json
    tickers_path = Path(__file__).parent.parent / "data" / "test_tickers.json"
    with open(tickers_path, "r") as f:
        data = json.load(f)
    
    # Iterate over tickers array
    tickers = data.get("tickers", [])
    for ticker in tickers:
        print(ticker)

    return {"message": "Updated"}
    
