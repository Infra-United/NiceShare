"""Magic Link Handler."""
from pathlib import Path

from nicegui import app, json, ui
from slugify import slugify

from niceshare.helper.config import settings
from niceshare.helper.paths import get_path


def get_magic_link() -> str:
    """Generates a magic link for sharing active cart contents..

    Returns:
        str: The link with user ID token

    """
    return f"{settings.domain}/{slugify(settings.cart['label'])}?id={app.storage.browser['id']}"


def load_data_from_magic_link(new_id: str) -> None:
    """Load user/cart data from given magic link.

    Args:
        new_id (str): The ID from the link

    """
    try:
        with Path.open(get_path(f"storage-user-{new_id}.json", "users"), "r") as f:
            app.storage.user.update(json.loads(f.read()))
            app.storage.browser.update({"id": new_id})
            ui.navigate.reload()
    except FileNotFoundError:
        ui.notify(f"Sorry, couldn't find data for =id?{new_id}.", type="negative", position="center", text="secondary")
        ui.timer(5, lambda: ui.navigate.to("/"), once=True)


