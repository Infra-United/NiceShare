"""Form Value Validation Module (Email Adress, Phone Number, Web URL)."""
import re
from collections.abc import Callable
from typing import Any, Final

from email_validator import EmailNotValidError, validate_email
from nicegui.observables import ObservableDict

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n

INPUT_VALIDATION: Final[dict[str, Callable[[str], bool]]] = {i18n.get("form.please_fill_field"): lambda v: len(v) > 0}
IMG_URL_REGEX: re.Pattern = re.compile(
    r"^(?P<url>(?P<domain>https?://[-a-zA-Z0-9@:%._\+~#=]+)(?P<path>(?P<subfolders>(?:/[-a-zA-Z0-9@:%._\+~#=]+)*/)?/?(?P<filename>[^\s/]+?\.(?P<ext>jpg|jpeg|png|gif|bmp|tiff|webp))))",
re.IGNORECASE)
URL_REGEX: re.Pattern = re.compile(r"^(https):\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[^\s]*)?$")


def validate_mail(key: str, email: str, request: ObservableDict) -> Any | None: 
    """Email Validation (Form and deliverability).

    Args:
        key (str): Field key for error messaging
        email (str): The Email Adress to validate
        request (ObservableDict): Form Data
    
    Returns:
        Any | None: Error message if failed, None otherwise

    """
    try:
        request.update({key: validate_email(email, check_deliverability=True, strict=True).normalized})
    except EmailNotValidError as e:
        return e.args[0]

def validate_number(key: str, donation: str, request: ObservableDict) -> Any | None:
    """Validates the donation value.

    Checks for real, larger then zero numbers.

    Args:
        key (str): Field key for error messaging
        donation (str): Donation value to validate
        request (ObservableDict): Form Data
    
    Returns:
        Any | None: Error message if failed, None otherwise

    """
    try:
        request.update({key: int(donation)})
    except ValueError:
        return i18n.get("form.number_invalid")

def validate_url(url: str, data:dict[str, str]) -> Any | None:
    """URL Validation and data update (if valid).

    Args:
        url (str): URL to validate
        data (dict[str, str]): Form data #TODO Why is this taking a different dict

    Returns:
        Any | None: Error message if failed, None otherwise
    
    """
    try:
        url = URL_REGEX.match(url).string
        data[settings.columns.get("url")] = url
    except AttributeError:
        return i18n.get("admin.url_invalid")
