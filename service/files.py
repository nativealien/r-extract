import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data/markets"

def get_ticker_path(exchange: str, ticker: str, file_name: str, file_extension: str = "csv") -> Path:

    return DATA_DIR / exchange.lower() / ticker.upper() / f"{file_name}.{file_extension}"

def load_symbols(type: str = "test") -> list[str]:
    
    if type == "test":
        file_path = Path(__file__).parent.parent / "data" / "tickers" / "test_tickers.json"
    elif type == "nasdaq":
        file_path = Path(__file__).parent.parent / "data" / "tickers" / "nasdaq_tickers.json"
    else:
        raise ValueError(f"Invalid type: {type}")


    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def add_symbols(type: str = "test", tickers: list[str] = []) -> None:
    if type == "test":
        file_path = Path(__file__).parent.parent / "data" / "tickers" / "test_tickers.json"
    elif type == "nasdaq":
        file_path = Path(__file__).parent.parent / "data" / "tickers" / "nasdaq_tickers.json"
    else:
        raise ValueError(f"Invalid type: {type}")

    # Load existing tickers
    existing_tickers = load_symbols(type)
    
    # Merge with new tickers (avoid duplicates)
    all_tickers = list(set(existing_tickers + tickers))
    
    # Write back to file
    with open(file_path, "w") as f:
        json.dump({"tickers": all_tickers}, f, indent=2)

def add_ticker(ticker, exchange, timeframe, data, info) -> None:
    path = get_ticker_path(exchange, ticker, timeframe, "csv")
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)

def update_ticker(ticker: str = None) -> None:
    if ticker is None:
        raise ValueError("Ticker is required")
    
    
