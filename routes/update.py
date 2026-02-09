import os
import json
import pandas as pd
# from pathlib import Path
from fastapi import APIRouter, Header, HTTPException
from dotenv import load_dotenv
from loguru import logger

from service.files import load_symbols, get_ticker_path, add_ticker
from service.yf import get_meta, update_data, get_data

from service.time import should_update_timeframe

from data.static.static import TIMEFRAME_MAP

load_dotenv()

router = APIRouter(prefix="/update", tags=["update"])

@router.get("")
async def check_auth(x_api_key: str = Header(alias="X-API-Key")):

    key = os.getenv("API_KEY")

    if x_api_key != key:
        raise HTTPException(status_code=401, detail="Unauthorized")


    tickers = load_symbols('nasdaq')
    exchange = tickers.get('exchange')
    tickers = tickers.get('tickers')

    # Counters for summary
    total_count = len(tickers)
    updated_count = 0
    up_to_date_count = 0
    errors_count = 0

    for ticker in tickers:
        meta_path = get_ticker_path(exchange, ticker, "meta", "json")
        last_update = {}
        updated = False
        
        try:
            if meta_path.exists():
                last_update_path = get_ticker_path(exchange, ticker, "last_update", "json")
                
                # Load existing last_update.json if it exists
                if last_update_path.exists():
                    with open(last_update_path, "r") as f:
                        last_update = json.load(f)

                    for timeframe in TIMEFRAME_MAP.keys():
                        ticker_path = get_ticker_path(exchange, ticker, timeframe, "csv")
                        
                        # Check if timeframe exists in last_update
                        if timeframe not in last_update:
                            logger.error(f"Missing timeframe key in last_update.json for {ticker}, timeframe {timeframe}")
                            continue
                        
                        try:
                            if should_update_timeframe(exchange, timeframe, last_update):
                                data = update_data(ticker, timeframe, last_update[timeframe])
                                
                                if data is not None and not data.empty:
                                    # Ensure directory exists
                                    ticker_path.parent.mkdir(parents=True, exist_ok=True)
                                    
                                    # Read existing CSV if it exists
                                    if ticker_path.exists():
                                        existing_data = pd.read_csv(ticker_path)
                                        # Convert Date column to datetime for proper merging
                                        if 'Date' in existing_data.columns:
                                            existing_data['Date'] = pd.to_datetime(existing_data['Date'])
                                        if 'Date' in data.columns:
                                            data['Date'] = pd.to_datetime(data['Date'])
                                        
                                        # Merge: concatenate and remove duplicates based on Date
                                        combined_data = pd.concat([existing_data, data], ignore_index=True)
                                        # Remove duplicates, keeping last occurrence
                                        combined_data = combined_data.drop_duplicates(subset=['Date'], keep='last')
                                    else:
                                        combined_data = data
                                    
                                    # Sort by Date
                                    if 'Date' in combined_data.columns:
                                        combined_data = combined_data.sort_values('Date').reset_index(drop=True)
                                    
                                    # Save updated CSV
                                    combined_data.to_csv(ticker_path, index=False)
                                    
                                    # Update last_update with the new last date
                                    if 'Date' in combined_data.columns and not combined_data.empty:
                                        last_date = combined_data['Date'].iloc[-1]
                                        last_update[timeframe] = str(last_date)
                                    
                                    updated = True
                        except Exception as e:
                            logger.error(f"Error updating {ticker} {timeframe}: {e}")
                
                # Save last_update.json for this ticker
                if last_update:
                    last_update_path = get_ticker_path(exchange, ticker, "last_update", "json")
                    last_update_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(last_update_path, "w") as f:
                        json.dump(last_update, f, indent=2)

            else:
                # Initial setup - no metadata exists yet
                try:
                    meta_data = get_meta(ticker)
                    
                    for timeframe in TIMEFRAME_MAP.keys():
                        try:
                            data = get_data(ticker, timeframe)
                            ticker_path = get_ticker_path(exchange, ticker, timeframe, "csv")

                            if data is not None and not data.empty:
                                ticker_path.parent.mkdir(parents=True, exist_ok=True)
                                data.to_csv(ticker_path, index=False)
                                
                                # Get last date from the Date column
                                if 'Date' in data.columns and not data.empty:
                                    last_date = data['Date'].iloc[-1]
                                    last_update[timeframe] = str(last_date)
                                
                                updated = True
                        except Exception as e:
                            logger.error(f"Error initializing {ticker} {timeframe}: {e}")
                    
                    # Save metadata if available
                    if meta_data:
                        meta_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(meta_path, "w") as f:
                            json.dump(meta_data, f, indent=2)
                except Exception as e:
                    logger.error(f"Error initializing {ticker}: {e}")
            
            # Save last_update.json for this ticker
            if last_update:
                last_update_path = get_ticker_path(exchange, ticker, "last_update", "json")
                last_update_path.parent.mkdir(parents=True, exist_ok=True)
                with open(last_update_path, "w") as f:
                    json.dump(last_update, f, indent=2)
            
            # Log status and update counters
            if updated:
                logger.info(f"{ticker} updated")
                updated_count += 1
            else:
                logger.info(f"{ticker} up to date")
                up_to_date_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            errors_count += 1

    # Log summary
    logger.info(f"Total: {total_count} | Updated: {updated_count} | Up to date: {up_to_date_count} | Errors: {errors_count}")

    return {"message": "Updated"}
    
