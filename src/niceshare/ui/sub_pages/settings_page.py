"""Settings Sub-Page Module."""
from nicegui import ui
from nicegui.elements.drawer import LeftDrawer

from niceshare.helper.config import settings
from niceshare.helper.i18n import i18n
from niceshare.helper.logger import LOGGER
from niceshare.io.load_data import load_data_from_dav, load_wiki_from_dav
from niceshare.io.nextcloud_exporter import export_inventory_to_nc
from niceshare.io.warehouse import Warehouse
from niceshare.ui.auth import authenticate_user


def settings_page(ld: LeftDrawer, warehouses:list[Warehouse]) -> None:
    """Creates the settings sub-page.

    Args:
        ld (LeftDrawer): The Left Drawer to hide
        warehouses (list[Warehouse]): List of warehouses 

    """
    # Redirects users to login page if not logged in 
    if not authenticate_user():
        ui.notify(i18n.get("admin.not_admin"), color="negative", position="top")
        ui.navigate.to("/login")
    ld.hide()

    # Creates Settings Page
    ui.page_title(f"{settings.settings['label']}")
    LOGGER.debug("Creating settings page...")
    with ui.tab_panel("settings").classes("m-0 p-10 max-sm:pb-20 items-center w-full scroll h-dvh"):
        ui.label("Achtung: Alle Bilder, Links & Kommentare die hier hochgeladen wurden gehen verloren! Falls du etwas geändert hast, exportiere zunächst.")
        ui.button(i18n.get("settings.reload_dav"), icon='update',
                  on_click=lambda: load_data_from_dav(reload=True)
                ).props("text-color=secondary")
        ui.label("Achtung: Die Inventur in der Cloud wird überschrieben - wenn in der Zwischenzeit was geändert wurde, geht das verloren!")
        ui.button(i18n.get("settings.export_inventory"), icon='update',
                  on_click=lambda: export_inventory_to_nc(warehouses)
                ).props("text-color=secondary")
        if settings.help["wiki"]:
            ui.label("Hinweis: Wiki laden dauert ne halbe Minute, läuft im Hintergrund.")
            ui.button(i18n.get("settings.reload_wiki"), icon='update',
                  on_click=lambda: load_wiki_from_dav(reload=True)
                ).props("text-color=secondary")
