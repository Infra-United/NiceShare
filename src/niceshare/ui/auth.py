"""Module for handling JSon Web Tokens (JWT) for authenticating users."""
import datetime
import os

import jwt
from jwt import ExpiredSignatureError
from nicegui import Event

from niceshare.io.cache import Cache

authenticated = Event[bool]()

def create_jwt() -> str:
    """JWT Creator.

    Creates a new JWT with the current time and a delta of 6 hours

    Returns:
        str: Json Web Token 
    
    """
    data = {
        "exp": datetime.datetime.now() + datetime.timedelta(hours=6), #TODO Timezone
    }
    return jwt.encode(data, os.environ["UI_AUTH_SECRET"], algorithm="HS256")


def authenticate_user() -> bool:
    """User authentication using a created JWT.

    Catches KeyError and ExpiredSignatureError and returns it as failed authentication.

    Returns:
        bool: True if the user authenticated, false otherwise

    """
    try:
        if Cache.auth_token() is None:
            return False
        else:
            jwt.decode(Cache.auth_token(), os.environ["UI_AUTH_SECRET"], algorithms="HS256")
            return True
    except KeyError, ExpiredSignatureError:
        return False
