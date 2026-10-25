"""Mail Handler Module."""
import smtplib
import ssl
import traceback
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from enum import StrEnum
from pathlib import Path

#from dotenv.variables import Literal
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from niceshare.helper.config import settings
from niceshare.helper.dates import convert_dates
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER


class RequestType(StrEnum):
    """Request Type Enum."""
    request = "request"
    update = "update"
    delete = "delete"
    failure = "failure"


class MailServer(BaseSettings):
    """Reads basic Mail Settings from .env file."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str


def send_mail(
    request: dict[str, str | dict[str, str]],
    request_type: RequestType,
    filename: Path | None = None,
    exception: Exception | None = None,
    mail_server: MailServer = None,
) -> None:
    """Sends an email notification for a request.

    Args:
        request (dict[str, str | dict[str, str]]): Request data to include 
        request_type (RequestType): Request Type (request, update, delete, failure)
        filename (Path): Optional file (Path) to be attached to the email
        exception (Exception): Optional exeption to include for failure emails 
        mail_server (MailServer): Custom SMTP or default if none specified
    
    """
    mail_server = MailServer() if mail_server is None else mail_server #Default mail server

    LOGGER.debug("Connecting to SMTP Server...")
    email = request.get("email")
    user_id = request.get("edit_link").split("=")[-1]

    # Constructing the email
    mail = MIMEMultipart("mixed")
    mail.add_header("Subject", _create_subject(request, request_type))
    mail.add_header("From", f"{mail_server.user}")
    mail.add_header("Reply-To", f"{email}") 
    mail.add_header("Date", formatdate(localtime=True))
    mail.add_header("Message-ID", f"<{user_id}-{request.get(request_type)}@{mail_server.domain}>")

    # Handling non request type emails (update, delete, failure)
    if request_type != "request":
        mail.add_header("In-Reply-To", f"<{user_id}-{request.get(RequestType.request)}@{mail_server.domain}>")
        mail.add_header("References", f"<{user_id}-{request.get('request')}@{mail_server.domain}>")
    mail.add_header("Return-Path", mail_server.user)
    mail.add_header("Reply-To", f"{email}")
    # mail.attach(MIMEText(create_text("text", request, exception), "plain"))
    mail.attach(MIMEText(_create_text("html", request, exception), "html"))

    # Attaching file as payload 
    if filename is not None:
        with Path.open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename.name}")
        mail.attach(part)

    # Setting receiver and sending email
    receiver = [settings.mail["mail_to"], request.get("email")] if not exception else [settings.mail["admin"]]
    mail.add_header("To", ", ".join(receiver))

    if mail_server.port == 1025:
        # Proton mail bridge 
        with smtplib.SMTP(mail_server.domain, mail_server.port) as smtp:
            smtp.starttls()
            smtp.ehlo()
            smtp.set_debuglevel(1)

            LOGGER.debug("Logging into SMTP Client with credentials...")
            smtp.login(mail_server.user, mail_server.password)

            LOGGER.debug(f"Sending E-Mail to {receiver}...")
            smtp.ehlo()
            smtp.sendmail(str(mail_server.user), receiver, mail.as_string())
            LOGGER.debug("Quitting Connection to SMTP Server...")
    else:
        # Other emails
        with smtplib.SMTP_SSL(mail_server.domain, mail_server.port, context=ssl.create_default_context()) as smtp:
            smtp.ehlo()
            smtp.set_debuglevel(1)

            LOGGER.debug("Logging into SMTP Client with credentials...")
            smtp.login(mail_server.user, mail_server.password)

            LOGGER.debug(f"Sending E-Mail to {receiver}...")
            smtp.ehlo()
            smtp.sendmail(str(mail_server.user), receiver, mail.as_string())
            LOGGER.debug("Quitting Connection to SMTP Server...")


def _create_subject(request: dict[str, str | dict[str, str]], rtype: RequestType) -> str:
    """Creates an email subject line based on request type and dates.
    
    Args:
        request (dict[str, str | dict[str, str]]): The request data 
        rtype (RequestType): The Request type 
    
    Returns:
        str: Formatted subject string

    """
    _, _, month, year = convert_dates(request.get("dates"))
    if rtype == RequestType.update or rtype == RequestType.delete:
        return f"Re: [{i18n.get(f'mail.{rtype}')}] {request.get('name')} {month} {year}"
    return f"[{i18n.get(f'mail.{rtype}')}] {request.get('name')} {month} {year}"


def _create_text(
    ttype: Literal["text", "html"], request: dict[str, str | float | dict[str, str]], exception: Exception  # noqa: F821, UP037
) -> str:
    """Creates the email body text in plain or HTML format.

    Args:
        ttype (Literal["text", "html"]): If the text is using plain text or html
        request (dict[str, str | float | dict[str, str]]): The request dict
        exception (Exception): Optional exception to include in failure messages. 
    
    Returns:
        str: Formatted email body
    
    """
    newline = "\n" if ttype == "text" else "<br>"
    add: list[str] = []
    for key, value in request.items():
        match key:
            case "dates":
                start, end, _, _ = convert_dates(request.get("dates")) 
                add.append(f"{i18n.get('form.start')}: {start}")
                add.append(f"{i18n.get('form.end')}: {end}")
                continue
            case "message" | "start" | "end":
                continue
            case "request" | "update" | "delete":
                if value:
                    readable_dt = f"{datetime.fromtimestamp(value):{settings.date_format} {settings.time_format}}" #TODO fix thie timestamp
                    add.append(f"{i18n.get(f'mail.{key}')}: {readable_dt}")
            case "edit_link":
                if not request.get("delete"):
                    add.append(f"{i18n.get('finish.editing_link')}: <a href={value}>{value}</a>")
            case _:
                if key in settings.form["input"].keys():
                    add.append(f"{settings.form['input'].get(key)}: {value}")
    add.append(f"{newline}{newline}{settings.form.get('message')}: {newline}{newline}{request.get('message')}")
    add.append(newline)
    if exception:
        add.append(f"{newline}{newline}{list(exception.args)}: {newline}{newline}{traceback.format_exc()}")

    return newline.join(add)
