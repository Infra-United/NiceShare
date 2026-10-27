"""Main Entrypoint for the programm that starts up the UI and retrieves needet files."""
import asyncio
import locale
import os
from pathlib import Path

import jwt
from dotenv import dotenv_values, load_dotenv
from nicegui import app, ui

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.load_data import load_data_from_dav, load_wiki_from_dav
from niceshare.ui.root import root


def main():
    """Main Function. Retrieves Data and starts the UI.

    Creates base files if they are missing and nextcloud is disabled.
    """
    if Path(".env").exists():
        LOGGER.debug(".env file found.")
    else:
        LOGGER.warn("Creating default .env file")
        with Path.open("./.env", 'w') as file:
            file.write(
                """
                    #.env
                    # Nextcloud
                    NEXTCLOUD_TOKEN=my-super-secret-nextcloud-app-token
                    NEXTCLOUD_USER=exampleuser
                    NEXTCLOUD_DOMAIN=cloud.example.org

                    # UI
                    UI_STORAGE_SECRET=somerandomstringlongenoughtobesafe
                    UI_ADMIN_PASSWORD="some password you will use to log in to admin panel"
                    UI_AUTH_SECRET=somerandomstringlongerthan32characters

                    # Mail
                    MAIL_USER=user@example.org
                    MAIL_PORT=465
                    MAIL_PASSWORD="my super secret mail password"
                    MAIL_DOMAIN=mailserver.example.org
                """
            )

    if ARGS.no_nextcloud:
        # Creating default files if they do not exist
        for md in ["help", "warehouse", "start"]:
            if not Path("/files/pages/" + getattr(settings,md)["path"]).exists():
                LOGGER.info(f"Creating starting file {md}.md in files/pages/")
                with Path.open(f"./files/pages/{getattr(settings,md)["path"]}", 'w') as file:
                    file.write(f"{md}.md File \n Enter Information for the {md} here")
        if not Path("/files/pages/" + settings.form["terms"]["path"]).exists():
            LOGGER.info("Creating starting file form terms.md in files/pages")
            with Path.open(f"./files/pages/{settings.form["terms"]["path"]}", 'w') as file:
                file.write(f"{md}.md File \n Enter Information for the form terms here")

    # Attempt to fetch Data from nextcloud, then load them locally 
    warehouses, pages = asyncio.run(load_data_from_dav())
    
    # Load wiki if enabled
    if settings.help["wiki"]:
        wiki = asyncio.run(load_wiki_from_dav())
    else: wiki = None

    load_dotenv()
    LOGGER.debug(dotenv_values())

    if len(os.environ["UI_AUTH_SECRET"]) < 32:
        raise jwt.exceptions.InvalidKeyError("Auth Secret must be at least 32 characters long")
    
    locale.setlocale(locale.LC_TIME, settings.locale)
    storage_secret = os.environ["UI_STORAGE_SECRET"]
    os.environ.setdefault("NICEGUI_STORAGE_PATH", str(get_path("users")))

    app.add_static_file(local_file=get_path("manifest.json"), url_path="/helpers/manifest.json", strict=False)
    app.add_static_file(local_file=get_path("service_worker.js"), url_path="/helpers/service_worker.js", strict=False)
    app.add_static_file(local_file=get_path("favicon.png"), url_path="/favicon.ico", strict=False)

    Path("./files/splash/").mkdir(exist_ok=True,parents=True)
    Path("./files/icons/").mkdir(exist_ok=True,parents=True)
    app.add_static_files("/splash/", get_path("splash")) 
    app.add_static_files("/icons/", get_path("icons"))
    ui.run(
        root=lambda: root(warehouses, pages, wiki),
        language=settings.language,
        uvicorn_logging_level="debug" if ARGS.debug else "info",
        show=False,
        reload=ARGS.reload,
        uvicorn_reload_dirs=str(get_path("").parent.joinpath("src")),
        title=settings.title,
        favicon=get_path(settings.favicon),
        port=settings.port,
        uvicorn_reload_excludes=str(get_path("")),
        storage_secret=storage_secret if storage_secret else "12341232312",
    )
    LOGGER.debug("Successfully started UI.")


if __name__ in {"__main__", "__mp_main__"}:
    main()
