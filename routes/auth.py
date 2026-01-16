import os
from fastapi import APIRouter, Header, HTTPException
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("")
async def check_auth(x_api_key: str = Header(alias="X-API-Key")):

    key = os.getenv("API_KEY")

    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Authorized"}