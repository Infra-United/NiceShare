"""Help Sub-Page Module."""
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.ui.helper.markdown import render_markdown
from niceshare.ui.helper.reusable_elements import share_fab


async def help_page(ld: LeftDrawer, md: dict[str, str]) -> None:
    """Creates the help sub-page from markdown.

    Args:
        ld (LeftDrawer): The Left Drawer to hide
        md (dict[str, str]): Directory of markdown pages

    """
    ld.hide()
    ui.page_title(f"{settings.help['label']}")
    LOGGER.debug("Creating help page...")
    with ui.tab_panel("help").classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        render_markdown(md.get(settings.help["label"]))

async def wiki_page(name: str, content: str, ld: LeftDrawer, style: str) -> None:
    """Creates a wiki page with styled content.

    Args:
        name (str): Name of the wiki page
        content (str): HTML content of the page
        ld (LeftDrawer): Left drawer to hide 
        style (str): CSS styling string 

    """
    ld.hide()
    ui.page_title(f"{name.capitalize()}")
    LOGGER.debug(f"Creating wiki page {name}...")

    with ui.tab_panel(name).classes("m-0 p-0 max-sm:pb-20 items-center w-full scroll h-dvh"):
        if settings.help["wiki"]:
            html = ui.html(f"<head>{style}</head> {content}", sanitize=False)
            html.classes("mx-auto items-center px-8 sm:px-20 text-base/6")
            html.classes("hyphens-none sm:text-base/6 sm:antialiasing text-gray-300 max-w-180")
            share_fab(name, content)