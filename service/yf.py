import yfinance as yf
import pandas as pd
from loguru import logger

TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "1d": "1d",
    "1wk": "1wk",
}

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

        print(hist)

    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        return None

def update_data(ticker: str, timeframe: str = "1d", from_date: str = None, to_date: str = None) -> None:
    try:
        # TODO: If dates is within weekend, adjust to nearest weekday
        if from_date is None or to_date is None:
            raise ValueError("from_date and to_date are required")

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

        print(hist.empty)

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

update_data("AAPL", "5m", "2025-01-01", "2025-01-12")