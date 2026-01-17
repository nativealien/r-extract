import yfinance as yf
import pandas as pd
from datetime import datetime
from loguru import logger

from data.static.static import TIMEFRAME_MAP
from service.time import get_today_swedish_date


def _parse_date_string(date_str: str) -> str:
    """
    Parse a date/datetime string and return just the date part in YYYY-MM-DD format.
    Handles various formats including datetime strings with timezone info.
    """
    if not date_str:
        return None
    
    # Try parsing as ISO format datetime
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        pass
    
    # Try parsing as date only (YYYY-MM-DD)
    try:
        dt = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except (ValueError, IndexError):
        pass
    
    # Return first 10 characters if it looks like a date
    if len(date_str) >= 10:
        return date_str[:10]
    
    return date_str

def get_data(ticker: str, timeframe: str = "1d", period: str = "max") -> pd.DataFrame | None:
    try:

        yf_ticker = yf.Ticker(ticker)
        yf_timeframe = TIMEFRAME_MAP.get(timeframe, "1d")

        hist = yf_ticker.history(period=period, interval=yf_timeframe)
        hist.reset_index(inplace=True)

        if hist.empty:
            raise ValueError("No data found for the given dates")

        if 'Datetime' in hist.columns:
            hist.rename(columns={'Datetime': 'Date'}, inplace=True)
        elif 'Date' not in hist.columns and len(hist.columns) > 0:
            # If the first column is the date column but not named, rename it
            hist.rename(columns={hist.columns[0]: 'Date'}, inplace=True)

        hist = hist.drop(columns=['Dividends', 'Stock Splits'], errors='ignore')

        return hist

    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        return None

def update_data(ticker: str, timeframe: str = "1d", from_date: str = None, to_date: str = None) -> None:
    try:
        # TODO: If dates is within weekend, adjust to nearest weekday
        if to_date is None:
            today = get_today_swedish_date()
            to_date = today.strftime('%Y-%m-%d')
        else:
            # Parse to_date to extract just the date part
            to_date = _parse_date_string(to_date)
        
        if from_date is None:
            raise ValueError("from_date is required")
        
        # Parse from_date to extract just the date part
        from_date = _parse_date_string(from_date)

        yf_ticker = yf.Ticker(ticker)
        yf_timeframe = TIMEFRAME_MAP.get(timeframe, "1d")
        hist = yf_ticker.history(start=from_date, end=to_date, interval=yf_timeframe)
        hist.reset_index(inplace=True)

        if hist.empty:
            raise ValueError("No data found for the given dates")

        if 'Datetime' in hist.columns:
            hist.rename(columns={'Datetime': 'Date'}, inplace=True)
        elif 'Date' not in hist.columns and len(hist.columns) > 0:
            # If the first column is the date column but not named, rename it
            hist.rename(columns={hist.columns[0]: 'Date'}, inplace=True)

        hist = hist.drop(columns=['Dividends', 'Stock Splits'], errors='ignore')

        return hist

    except Exception as e:
        logger.error(f"Error updating data for {ticker}: {e}")
        return None

def get_meta(ticker: str) -> dict | None:
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        return info
    except Exception as e:
        logger.error(f"Error getting metadata for {ticker}: {e}")
        return None
