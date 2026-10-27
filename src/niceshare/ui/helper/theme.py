"""Them class / handling for ui."""
from typing import Self

from nicegui import ui

from niceshare.helper.config import settings


class Theme:
    """Theme styling class for managing UI color schemes."""
    instance = None

    def __init__(self, config: dict[str, str]) -> None:
        """Initializes the theme with color configuration.

        Args:
            config (dict[str,str]): Dictionary containing theme color settings.
            
        """
        self.primary = config.get("primary")
        self.secondary = config.get("secondary")
        self.accent = config.get("accent")
        self.dark_page = config.get("dark_page")
        self.links = config.get("links")
        self.dark_mode = config.get("dark_mode")

    @classmethod
    def singleton(cls) -> Self:
        """Returns the singleton instance of the Theme class.

        Returns:
            Self: The singleton Theme instance.

        """
        if not cls.instance:
            cls.instance = Theme(config=settings.theme)
        return cls.instance

    def set_colors(self):
        """Sets the colors for the theme and dark mode."""
        ui.colors(
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            dark_page=self.dark_page,
            links=self.links,
        ).update()
        ui.dark_mode(self.dark_mode)
