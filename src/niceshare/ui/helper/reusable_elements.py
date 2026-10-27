"""Module for reusable UI elements."""
from nicegui import app, ui
from nicegui.elements.badge import Badge
from nicegui.elements.tabs import Tabs
from slugify import slugify

from niceshare.helper.i18n import i18n
from niceshare.io.database import DB
from niceshare.io.warehouse import Warehouse
from niceshare.ui.helper.share import get_qr_code, share_content


def badge(text: str) -> Badge: 
    """Converts raw text to an ui badge.

    Args:
        text (str): Text to display

    Returns:
        Badge: UI Badge Element

    """
    return ui.badge(text, color="secondary", text_color="white").props().classes("text-bold ml-2 py-1")


def tabs() -> Tabs:
    """Creates styled navigation tabs.

    Returns:
        Tabs: Styled tab component

    """
    return (
        ui.tabs()
        .classes(
            "bg-secondary text-gray-200 h-[56px] w-full scroll font-bold subpixel-antialiased tracking-widest m-0 p-0"
        )
        .props("height=56px active-bg-color=accent inline-label mobile-arrows stretch")
    )


def tab_panels(_tabs: Tabs) -> tab_panels:
    """Creates tab panels linked to existing tabs.
    
    Args:
        _tabs (Tabs): Existing tabs

    Returns:
        tab_panels: Tab panels component

    """
    return ui.tab_panels(_tabs).classes("w-full h-dvh")

#fab = floating action button.
def next_fab(next_page: dict[str, str]) -> None:
    """Creates a floating action button for navigating to the next page.

    Args:
        next_page (dict[str, str]): Dict containing page label and icon 

    """
    props: str = "text-color=secondary"
    with ui.page_sticky(position="bottom-right", x_offset=18, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_next").props(f"{props} active-icon='hourglass_top'")
        fab.on("click", lambda: ui.navigate.to(f"/{slugify(next_page['label'])}?id={app.storage.browser['id']}"))
        fab.on("mouseenter", lambda: label.set_visibility(True), throttle=0.2)
        fab.on("mouseleave", lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot("label"):
            with ui.row():
                ui.icon(next_page["icon"])
                label = ui.label(next_page["label"]).classes("text-secondary text-base")
                label.set_visibility(False)
            badge = (
                ui.badge("0", color="primary", text_color="secondary").props("rounded floating").classes("text-bold")
            )
            badge.bind_text_from(app.storage.user, "Total")
            badge.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)


def back_fab(last_page: dict[str, str]) -> None:
    """Creates a floating action button for navigating to the previous page.

    Args:
        las_page (dict[str, str]): Dict containing page label and icon 

    """
    props: str = "text-color=primary"
    with ui.page_sticky(position="bottom-left", x_offset=30, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="navigate_before", color="secondary").props(f"{props}")
        fab.on("click", lambda: ui.navigate.to(f"/{slugify(last_page['label'])}?id={app.storage.browser['id']}"))
        fab.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)
        fab.on("mouseenter", lambda: label.set_visibility(True), throttle=0.2)
        fab.on("mouseleave", lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot("label"):
            with ui.row():
                ui.icon(last_page["icon"])
                label = ui.label(last_page["label"]).classes("text-base")
                label.set_visibility(False)
            badge = (
                ui.badge("0", color="secondary", text_color="primary").props("rounded floating").classes("text-bold")
            )
            badge.bind_text_from(app.storage.user, "Total")
            badge.bind_visibility_from(app.storage.user, "Total", backward=lambda v: v > 0)

def share_fab(name:str, content:str) -> None:
    """Creates a floating action button for sharing content.

    Args:
        name (str): Name of the content
        content (str): The content to share

    """
    with ui.page_sticky(x_offset=40, y_offset=40):
        with ui.fab(icon='share', direction='up'):
            ui.fab_action(icon='link').on('click', lambda: share_content(name, content)).props('active-icon=share')
            ui.fab_action(icon='description').on('click', lambda: share_content(name, content, verbose=True)).props(
                'active-icon=share')
            ui.fab_action(icon='qr_code').on('click', lambda: get_qr_code(name)).props('active-icon=share')


def save_fab(warehouse: Warehouse) -> None:
    """Creates a floating action button for saving warehouse data.

    Args:
        warehouse (Warehouse): Warehouse instance to save

    """
    async def save_data():
        DB.save(warehouse.name, warehouse.inventory, 'inventory')
        ui.navigate.reload()

    with ui.page_sticky(position="bottom-right", x_offset=18, y_offset=18).classes("z-999"):
        fab = ui.fab(icon="expand_more").props("text-color=secondary active-icon='hourglass_top'")
        fab.on("click", save_data)
        fab.on("mouseenter", lambda: label.set_visibility(True), throttle=0.2)
        fab.on("mouseleave", lambda: label.set_visibility(False), throttle=0.2)
        with fab.add_slot("label"):
            with ui.row():
                ui.icon('save')
                label = ui.label(i18n.get("admin.save")).classes("text-secondary text-base")
                label.set_visibility(False)


