"""Module for caching stuff."""
from nicegui import app
from nicegui.observables import ObservableDict, ObservableList

from niceshare.helper.i18n import i18n


class Cache:
    """Cache Class for storing data in memory (browser tab)."""
    def __init__(self, warehouses:list[Warehouse]): #TODO how to fix without circle import?s
        """Init for Cache.

        Args:
            warehouses (list[Warehouse]): A list of warehouses 

        """
        app.storage.user.indent = True
        app.storage.user.setdefault("Total", 0)
        app.storage.user.setdefault("width", 0)
        app.storage.user.setdefault(
            "form",
            {
                "dates": None,
                "name": "",
                "place": "",
                "donation": "",
                "email": "",
                "message": "",
                "messenger": "",
                "request": None,
                "update": None,
                "finish": None,
                "edit_link": None,
                "overlap": i18n.get("finish.no_overlap"),
            },
        )
        app.storage.user.setdefault("notified", None)
        app.storage.user.setdefault("selected", {})
        app.storage.user.setdefault("added", {})
        app.storage.user.setdefault("deleted", {})
        app.storage.user.setdefault("edited", {})
        app.storage.user.setdefault("amounts", {})
        app.storage.user.setdefault("weight", {})
        for warehouse in warehouses:
            app.storage.user["selected"].update({warehouse.name: []}) if not self.selected(warehouse.name) else None
            app.storage.user["added"].update({warehouse.name: []}) if not self.added(warehouse.name) else None
            app.storage.user["deleted"].update({warehouse.name: []}) if not self.deleted(warehouse.name) else None
            app.storage.user["edited"].update({warehouse.name: {}}) if not self.edited(warehouse.name) else None
            app.storage.user["amounts"].update({warehouse.name: {}}) if not self.amounts(warehouse.name) else None

    @classmethod
    def total(cls) -> int:
        """Getter for the total weight.

        Returns:
            int: Total weight

        """
        return int(app.storage.user["Total"])

    @classmethod
    def width(cls) -> int:
        """Getter for width.

        Returns:
            width: width in cm

        """
        return int(app.storage.user["width"])

    @classmethod
    def set_width(cls, width: int) -> None:
        """Setter for width.

        Args:
            width (int): The new width

        """        
        app.storage.user["width"] = width

    @classmethod
    def notified(cls) -> bool:
        """Getter for the user notiefied flag.

        Returns:
            bool: If the user is notified

        """        
        return app.storage.user["notified"]

    @classmethod
    def form(cls) -> ObservableDict:
        """Getter for user form.

        Returns:
            ObservableDict: The currently active form of the user

        """        
        return app.storage.user["form"]

    @classmethod
    def amounts(cls, name: str) -> ObservableDict:
        """Getter for the name of an item.

        Args:
            name (str): The name of the item

        Returns:
            ObservableDict: The amounts of the item

        """        
        return app.storage.user["amounts"].get(name)

    @classmethod
    def deleted(cls, name: str) -> ObservableList:
        """Getter for deleted.

        Args:
            name (str): The name of the deleted things
        
        Returns:
            ObservableList: The Data

        """        
        return app.storage.user["deleted"].get(name)

    @classmethod
    def added(cls, name: str) -> ObservableList:
        """Getter for TEXT..

        Returns:

        """        
        return app.storage.user["added"].get(name)

    @classmethod
    def edited(cls, name: str) -> ObservableDict:
        """Getter for TEXT..

        Returns:

        """        
        return app.storage.user["edited"].get(name)

    @classmethod
    def selected(cls, name: str) -> ObservableList:
        """Getter for TEXT..

        Returns:

        """        
        return app.storage.user["selected"].get(name)

    @classmethod
    def weight(cls, name):
        """Getter for TEXT..

        Returns:

        """        
        return app.storage.user["weight"].get(name)

    @classmethod
    def set_weight(cls, name, weight: float):
        """Getter for TEXT..

        Returns:

        """        
        app.storage.user["weight"][name] = weight

    @classmethod
    def auth_token(cls) -> str | None:
        """Getter for TEXT..

        Returns:

        """        
        return app.storage.user.get("auth_token")
