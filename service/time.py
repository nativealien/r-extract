from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from data.static.static import EXCHANGE_TIMEZONES, MARKET_HOURS


def get_swedish_time() -> datetime:
    """Get current datetime in Swedish timezone (CET/CEST)."""
    return datetime.now(ZoneInfo("Europe/Stockholm"))


def get_today_swedish_date() -> datetime:
    """Get today's date in Swedish timezone (date only, time set to 00:00)."""
    swedish_now = get_swedish_time()
    return swedish_now.replace(hour=0, minute=0, second=0, microsecond=0)


def is_session_ended(exchange: str, check_date: datetime = None) -> bool:
    """
    Check if the trading session has ended for a given exchange on a specific date.
    
    Args:
        exchange: Exchange code (e.g., "NMS", "NYQ")
        check_date: Date to check (defaults to today in Swedish timezone)
    
    Returns:
        True if session has ended, False otherwise
    """
    if check_date is None:
        check_date = get_swedish_time()
    else:
        # Ensure check_date is timezone-aware in Swedish time
        if check_date.tzinfo is None:
            check_date = check_date.replace(tzinfo=ZoneInfo("Europe/Stockholm"))
    
    if exchange not in MARKET_HOURS:
        raise ValueError(f"Unknown exchange: {exchange}")
    
    # Get market hours: (open_hour, open_minute, close_hour, close_minute, offset_minutes)
    _, _, close_hour, close_minute, offset_minutes = MARKET_HOURS[exchange]
    
    # Calculate market close time in Swedish timezone
    # offset_minutes converts from exchange local time to Swedish time
    # For US markets: close at 16:00 EST = 22:00 CET (16:00 + 6 hours = 22:00)
    market_close_swedish = check_date.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)
    market_close_swedish += timedelta(minutes=offset_minutes)
    
    # Check if current Swedish time is past the market close time
    current_swedish = get_swedish_time()
    
    # Only check if it's a weekday (Monday=0, Sunday=6)
    if current_swedish.weekday() >= 5:  # Saturday or Sunday
        return False
    
    return current_swedish >= market_close_swedish


def is_weekday(date: datetime) -> bool:
    """Check if a date is a weekday (Monday-Friday)."""
    return date.weekday() < 5


def get_trading_days_between(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Get list of trading days (weekdays) between two dates (inclusive).
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
    
    Returns:
        List of trading day datetimes
    """
    if start_date > end_date:
        return []
    
    trading_days = []
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    while current <= end:
        if is_weekday(current):
            trading_days.append(current)
        current += timedelta(days=1)
    
    return trading_days


def get_last_friday_of_week(date: datetime) -> datetime:
    """Get the Friday of the week containing the given date."""
    days_until_friday = (4 - date.weekday()) % 7
    if days_until_friday == 0 and date.weekday() == 4:
        return date  # Already Friday
    friday = date + timedelta(days=days_until_friday if days_until_friday > 0 else 0)
    return friday.replace(hour=0, minute=0, second=0, microsecond=0)


def is_week_fully_closed(exchange: str, week_end_date: datetime = None) -> bool:
    """
    Check if a trading week has fully closed.
    A week is considered closed if:
    1. It's Monday (or later) in Swedish time
    2. The previous Friday's session has ended
    
    Args:
        exchange: Exchange code
        week_end_date: The Friday date to check (defaults to last Friday)
    
    Returns:
        True if the week is fully closed, False otherwise
    """
    swedish_now = get_swedish_time()
    
    # If today is Monday or later, check if last Friday's session ended
    if week_end_date is None:
        if swedish_now.weekday() == 0:  # Monday
            # Check last Friday (3 days ago)
            last_friday = swedish_now - timedelta(days=3)
        elif swedish_now.weekday() >= 1:  # Tuesday onwards
            # Check if we're past Monday, so last Friday was definitely closed
            # But still verify the session ended
            days_since_friday = (swedish_now.weekday() + 3) % 7
            if days_since_friday == 0:
                days_since_friday = 7
            last_friday = swedish_now - timedelta(days=days_since_friday)
        else:  # Sunday
            return False  # Week hasn't started yet
        week_end_date = last_friday
    else:
        week_end_date = week_end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if that Friday's session has ended
    return is_session_ended(exchange, week_end_date)


def get_dates_to_update(
    exchange: str,
    last_update_date: str,
    timeframe: str,
    today_date: datetime = None
) -> list[datetime]:
    """
    Get list of dates that need to be updated for a given timeframe.
    Only returns dates for sessions that have definitely ended.
    
    Args:
        exchange: Exchange code
        last_update_date: Last update date as string (from last_update.json)
        timeframe: Timeframe code (e.g., "1d", "1wk")
        today_date: Today's date in Swedish timezone (defaults to current)
    
    Returns:
        List of dates that need updating (empty if nothing to update)
    """
    if today_date is None:
        today_date = get_today_swedish_date()
    
    # Parse last_update_date string to datetime
    try:
        # Try parsing as ISO format datetime
        last_update = datetime.fromisoformat(last_update_date.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            # Try parsing as date only
            last_update = datetime.strptime(last_update_date, '%Y-%m-%d')
        except ValueError:
            return []
    
    # Ensure timezone-aware
    if last_update.tzinfo is None:
        last_update = last_update.replace(tzinfo=ZoneInfo("Europe/Stockholm"))
    
    # Ensure today_date is timezone-aware
    if today_date.tzinfo is None:
        today_date = today_date.replace(tzinfo=ZoneInfo("Europe/Stockholm"))
    
    if timeframe == "1wk":
        # Special handling for weekly timeframe
        if not is_week_fully_closed(exchange):
            return []
        
        # Get the last complete week's Friday
        last_friday = get_last_friday_of_week(today_date - timedelta(days=7))
        
        # Only update if last_update is before last Friday
        if last_update.date() < last_friday.date():
            return [last_friday]
        return []
    
    else:
        # For other timeframes (1m, 5m, 15m, 1h, 1d)
        # Get all trading days between last_update and today
        trading_days = get_trading_days_between(last_update, today_date)
        
        # Filter out today if today's session hasn't ended
        dates_to_update = []
        for day in trading_days:
            # Skip today if session hasn't ended
            if day.date() == today_date.date():
                if not is_session_ended(exchange, day):
                    continue
            dates_to_update.append(day)
        
        # Remove last_update date itself (we already have that data)
        if dates_to_update and dates_to_update[0].date() == last_update.date():
            dates_to_update.pop(0)
        
        return dates_to_update


def should_update_timeframe(
    exchange: str,
    timeframe: str,
    last_update_dict: dict,
    today_date: datetime = None
) -> bool:
    """
    Quick check if a timeframe needs updating based on last_update.json.
    
    Args:
        exchange: Exchange code
        timeframe: Timeframe code
        last_update_dict: Dictionary from last_update.json
        today_date: Today's date (defaults to current)
    
    Returns:
        True if timeframe needs updating, False otherwise
    """
    if timeframe not in last_update_dict:
        return True  # Never updated before
    
    dates_to_update = get_dates_to_update(
        exchange,
        last_update_dict[timeframe],
        timeframe,
        today_date
    )
    
    return len(dates_to_update) > 0
