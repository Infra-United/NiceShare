"""Login Sub Page Module."""
import os
import time

from nicegui import app, ui

from niceshare.ui.auth import create_jwt
from niceshare.ui.layout import drawer_menu, main_menu


def login_page() -> None:
    """Login Page Constructor.
    
    Manages the safe User Login

    """
    app.storage.user.update({"auth_token": None})
    main_menu.refresh()
    drawer_menu.refresh()

    with ui.tab_panel("default").classes("m-0 w-full h-dvh text-secondary decoration-primary"):
        with ui.card().classes("mx-auto my-auto"):
            pw_in = ui.input("Password", password=True, password_toggle_button=True)
            ui.button(
                "Log in",
            ).on("click", lambda: login(pw_in.value)).classes("mx-auto")

    async def login(password: str):
        if os.environ["UI_ADMIN_PASSWORD"] == password:
            token = create_jwt()
            app.storage.user.update({"auth_token": token})
            await main_menu.refresh()
            await drawer_menu.refresh()
            ui.navigate.to("/")
        else:
            time.sleep(1) #TODO bad
            pw_in.set_value("")
            ui.notify("This password is incorrect.", color="negative")
