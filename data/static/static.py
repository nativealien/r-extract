

TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "1d": "1d",
    "1wk": "1wk",
}

TIMEFRAME_DURATIONS = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "1d": 1440,  # 24 hours
    "1w": 10080,  # 7 days
}

EXCHANGE_TIMEZONES = {
    "NMS": "America/New_York",
    "NYQ": "America/New_York",
    "LON": "Europe/London",
    "FRA": "Europe/Berlin",
    "STO": "Europe/Stockholm",
    "PAR": "Europe/Paris",
    "TYO": "Asia/Tokyo",
    "HKG": "Asia/Hong_Kong",
    "TSE": "America/Toronto",
}

EXCHANGES = {
    "NMS": "Nasdaq",
    "NYQ": "NYSE",
    "LON": "London Stock Exchange",
    "FRA": "Frankfurt Stock Exchange",
    "STO": "Stockholm Stock Exchange",
    "PAR": "Paris Stock Exchange",
    "TYO": "Tokyo Stock Exchange",
    "HKG": "Hong Kong Stock Exchange",
    "TSE": "Toronto Stock Exchange",
}

# Market hours mapping (exchange code -> (open_hour, open_minute, close_hour, close_minute, offset_minutes))
# offset_minutes: minutes to add/subtract to convert exchange local time to Swedish time (CET/CEST)
MARKET_HOURS = {
    "NMS": (9, 30, 16, 0, 360),   # NASDAQ (EST/EDT -> CET/CEST: +6 hours)
    "NYQ": (9, 30, 16, 0, 360),   # NYSE (EST/EDT -> CET/CEST: +6 hours)
    "LON": (8, 0, 16, 30, 60),    # London (GMT/BST -> CET/CEST: +1 hour)
    "FRA": (9, 0, 17, 30, 0),     # Frankfurt (same timezone as Sweden)
    "STO": (9, 0, 17, 30, 0),     # Stockholm (same timezone as Sweden)
    "PAR": (9, 0, 17, 30, 0),     # Paris (same timezone as Sweden)
    "TYO": (9, 0, 15, 0, -480),   # Tokyo (JST -> CET/CEST: -8 hours)
    "HKG": (9, 30, 16, 0, -420),  # Hong Kong (HKT -> CET/CEST: -7 hours)
    "TSE": (9, 30, 16, 0, 360),   # Toronto (EST/EDT -> CET/CEST: +6 hours)
}