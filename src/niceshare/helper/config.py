"""Config / Settings Module."""
from logging import debug, exception, warning
from pathlib import Path
from typing import Self

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource

from niceshare.cli import ARGS
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path

CONFIG_FILE: Path = get_path(ARGS.config_file) #The User created config file 
DEFAULT_CONFIG_FILE: Path = get_path("default_config.yml") #Default fallback file


class Settings(BaseSettings):
    """Base Config Creator.

    Creates the config file from hardcodet variables. Any changes to the default should be made here

    """
    model_config = SettingsConfigDict(
        yaml_file=CONFIG_FILE,
        # yaml_config_section='',
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs) -> YamlConfigSettingsSource:
        """Applies custom sources to an existing config source.
    
        Args:
            settigs_cls: The original settings objet
            **kwargs: Arguments to apply 
    
        Returns:
            YamlConfigSettingsSource: The Updates Settings
    
        """
        return (YamlConfigSettingsSource(settings_cls),)

    title: str = "InventurGui"
    logo: str = "logo.png"
    favicon: str = "favicon.png"
    organization: str = "example"
    domain: str = "https://inventur.example.org"
    port: int = 8080
    language: str = "en"
    locale: str = "en_US.UTF-8"
    date_format: str = "%m/%d/%Y"
    time_format: str = "%H:%M"
    theme: dict[str, str | bool] = {
        "primary": "#e89769",
        "secondary": "#37474f",
        "accent": "#607d8b",
        "dark_page": "#0d1626",
        "dark_mode": True,
    }
    dav: dict[str, str | float | dict[str, str]] = {
        "dir": "InventurGui",
        "pull": {
            "logo": "logo.jpeg",
            "help": "help.md",
            "terms": "terms.md",
            "start": "start.md",
            "inventory": "inventory.xlsx",
        },
    }
    data: dict[str, str | int | list[str] | dict[str, str]] = {
        "filename": "inventory",
        "warehouses": [""],
        "columns": {
            "shelf": "Shelf",
            "category": "Category",
            "object": "Name",
            "count": "Amount",
            "total": "of",
            "pack": "Package",
            "weight": "Weight",
            "total_weight": "Total Weight",
            "comment": "Comment",
            "image": "Image",
            "url": "url",
        },
    }
    @property
    def columns(self) -> dict[str, str]:
        """Getter for the columns data.

        Returns:
            dict[str, str]: The inventory data as used in the (excel) file
        """
        return self.data["columns"]

    @property
    def data_filename(self) -> str:
        """Getter for the filename.

        Returns:
            str: The filename 
        """
        return self.data["filename"]
    mail: dict[str, str] = {
        "mail_to": "hello@example.org",
        "admin": "admin@example.org"
    }
    start: dict[str, str | bool] = {
        "label": "Start",
        "icon": "home",
        "path": "about.md"
    }
    help: dict[str, str | bool] = {
        "display": True,
        "wiki": False,
        "label": "Help",
        "icon": "help_outline",
        "path": "help.md",
    }
    warehouse: dict[str, str | bool] = {
        "label": "Lager",
        "display": True,
        "icon": "warehouse",
        "path": "lager.md",
        "everything": "Everything",
        "selection": "My Selection",
    }
    cart: dict[str, str] = {
        "label": "Cart",
        "icon": "cart",
        "tab_icon": "local_shipping",
    }
    form: dict[str, str | dict[str, str | bool]] = {
        "label": "Form",  # The url path of the requests page
        "icon": "article",  # The menu icon for the requests page
        "tab_label": "Form",  # The label for the form tab on the page
        "tab_icon": "article",  # The icon for the form tab on the page
        # Form Fields
        "from": "Pick-Up",
        "to": "Return",
        "input": {
            "name": "Name",  # This field is required
            "place": "Ort",
            "donation": "Donation",
            "email": "E-Mail",
            "messenger": "Messenger-Contact (Signal, etc.)",
        },
        "message": "Your Message - Questions, Notes and important Infos",
        "checkbox": {"terms": "I have read the terms."},
        "terms": {  # Show terms to the user in a tab next to the form
            "display": True,  # Set this to false if you don't need this
            "label": "Terms",
            "icon": "policy",
            "path": "terms.md",
        },
    }
    finish: dict[str, str] = {"label": "Finish"}
    requests: dict[str, str] = {  # Only visible for admins and editors
        "label": "Requests",
        "icon": "drafts",
        "filename": "requests",
    }
    settings: dict[str, str] = {
        "label": "Settings",
    }

    @classmethod
    def load_config(cls) -> Self:
        """Loads the config from file.

        The file to load from is specified through the argument parser (CLI)

        """
        debug(f"Loading config from {CONFIG_FILE}...")
        try:
            with Path.open(CONFIG_FILE, "r") as file:
                return Settings(**yaml.load(file, yaml.SafeLoader))
        except FileNotFoundError:
            warning("File not Found - Loading default-config:", CONFIG_FILE)
        except yaml.YAMLError as e:
            exception("Error in config file: \n" + e.args[0]), file.close()
        # Load Default if customized is failing 
        with Path.open(DEFAULT_CONFIG_FILE, "r") as file:
            return Settings(**yaml.load(file, yaml.SafeLoader))

    # TODO This looked unused, what should it be used for? - P
    # def dump_config(self) -> None:
    #     debug(f"Dumping config to {CONFIG_FILE}...")
    #     try:
    #         with open(CONFIG_FILE, "w") as file:
    #             yaml.dump(self.model_dump(), file, yaml.SafeDumper)
    #     except FileNotFoundError:
    #         exception("File not Found:", CONFIG_FILE), exit(1)
    #     except yaml.YAMLError as e:
    #         exception("Error in config: \n" + e.args[0]), file.close(), exit(1)

    @classmethod
    def create_default_config(cls) -> None:
        """Creates a default config file from code."""
        LOGGER.debug(f"Dumping default config to {DEFAULT_CONFIG_FILE}...")
        if DEFAULT_CONFIG_FILE.is_file():
            DEFAULT_CONFIG_FILE.unlink()
        with Path.open(DEFAULT_CONFIG_FILE, "w") as file:
            file.write(yaml.dump(Settings().model_dump(), Dumper=yaml.SafeDumper, sort_keys=False))
        LOGGER.info(f"Successfully wrote default config to {DEFAULT_CONFIG_FILE}.")

if not CONFIG_FILE.is_file():
    Settings.create_default_config()
    LOGGER.warn(f"Please copy {DEFAULT_CONFIG_FILE} to {CONFIG_FILE} and edit it to your needs!")
    exit(0)
settings = Settings.load_config()
