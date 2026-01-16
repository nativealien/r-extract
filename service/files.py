import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data/markets"

def get_ticker_path(exchange: str, ticker: str, file_name: str, file_extension: str = "csv") -> Path:

    return DATA_DIR / exchange.lower() / ticker.upper() / f"{file_name}.{file_extension}"

def load_tickers(type: str = "test") -> list[str]:
    
    if type == "test":
        file_path = Path(__file__).parent.parent / "data" / "test_tickers.json"
    elif type == "nasdaq":
        file_path = Path(__file__).parent.parent / "data" / "nasdaq_tickers.json"
    else:
        raise ValueError(f"Invalid type: {type}")


    with open(file_path, "r") as f:
        data = json.load(f)
    return data.get("tickers", [])


def add_tickers(type: str = "test", tickers: list[str] = []) -> None:
    if type == "test":
        file_path = Path(__file__).parent.parent / "data" / "test_tickers.json"
    elif type == "nasdaq":
        file_path = Path(__file__).parent.parent / "data" / "nasdaq_tickers.json"
    else:
        raise ValueError(f"Invalid type: {type}")

    # Load existing tickers
    existing_tickers = load_tickers(type)
    
    # Merge with new tickers (avoid duplicates)
    all_tickers = list(set(existing_tickers + tickers))
    
    # Write back to file
    with open(file_path, "w") as f:
        json.dump({"tickers": all_tickers}, f, indent=2)
