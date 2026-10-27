"""Date Converter helper."""
from datetime import date

from niceshare.helper.config import settings


def convert_dates(dates: str | dict[str, str], string:bool=True) -> tuple[str | date, str | date, str, str]:
    """Converts the dates supplied from a date_range_picker to the configured format.
    
    Also returns the month (%B) and year (%y) of the range.
    See https://strftime.org/ for more information.

    Args:
        dates (str | dict[str, str]): {'from': start, 'to': end}
        string (bool): True if start and end should be converted to a string. False to return them as date object.
        
    Returns:
       Tuple[str | date, str | date, str, str]: Tuple of date time in desired format 

    """
    if isinstance(dates, dict):
        start = dates.get("from")
        end = dates.get("to")
    else:
        start = dates
        end = dates
    start = date.fromisoformat(start)
    end = date.fromisoformat(end)
    year = f"{start:%y}/{end:%y}" if not start.year == end.year else f"{start:%y}"
    month = f"{start:%B}/{end:%B}" if not start.month == end.month else f"{start:%B}"
    if string:
        start = start.strftime(settings.date_format)
        end = end.strftime(settings.date_format)
    return start, end, month, year
