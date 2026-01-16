import os
# import json
# from pathlib import Path
from fastapi import APIRouter, Header, HTTPException
from dotenv import load_dotenv
from loguru import logger

from service.files import load_tickers

load_dotenv()

router = APIRouter(prefix="/update", tags=["update"])

@router.get("")
async def check_auth(x_api_key: str = Header(alias="X-API-Key")):

    key = os.getenv("API_KEY")

    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Unauthorized")


    tickers = load_tickers('test')
    for ticker in tickers:
        print(ticker)

    return {"message": "Updated"}
    
