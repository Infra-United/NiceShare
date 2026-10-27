"""Nectcloud Handling Module."""
from pathlib import Path
from typing import Self

import requests.exceptions
from pydantic_settings import BaseSettings, SettingsConfigDict
from webdav4.client import Client

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path


class NextcloudSettings(BaseSettings):
    """Nextcloud Settings read from .env file."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="UTF-8",
        env_prefix="NEXTCLOUD_",
        extra="ignore",
    )
    domain: str
    user: str
    token: str


class Nextcloud(Client):
    """Nextcloud instance."""

    instance = None

    def __init__(self, remote_dir: str, ncs: NextcloudSettings = None): 
        """Initializes a Nextcloud client instance.

        Args:
            remote_dir (str): Remote directory path on Nextcloud
            ncs (NextcloudSettings): Settings for Nextcloud

        """
        ncs = NextcloudSettings() if ncs is None else ncs
        self._domain = ncs.domain
        self._user = ncs.user
        self._webdav_url = f"https://{self._domain}/remote.php/dav/files/{self._user}"
        self.remote_dir = remote_dir
        super().__init__(self._webdav_url, auth=(self._user, ncs.token))

    @classmethod
    def singleton(cls) -> Self:
        """Returns the singleton instance of Nextcloud.
        
        Returns:
            Self: The Singleton Nextcloud instance.
        """
        if not cls.instance:
            cls.instance = Nextcloud(remote_dir=settings.dav["dir"])
        return cls.instance

    @staticmethod
    def shut_down_if_missing_file(path: Path) -> None:
        """Shuts down if a file is missing.
        
        Args:
            path (Path): The path to the required file 

        """
        if not path.is_file():
            LOGGER.exception(f"\nFile: >>>{path}<<< does not exist.\n Shutting down.")
            exit(1)

    def pull_files(self) -> None:
        """Pull files (multible) from remote."""
        for key, file in settings.dav["pull"].items():
            self.pull_file(key, file)

    def pull_file(self, key: str, file: str) -> None:
        """Pull a specific (singular) file from the remote.

        Args:
            key (str): Identifier for the file 
            file (str): Remote file path
        
        """
        if key in ["inventory", "logo"]:
            local = get_path(Path(file).name)
        else:
            local = get_path(Path(file).name, "pages")
        remote = "/".join((self.remote_dir, file))
        try:
            if self.exists(remote):
                LOGGER.debug(f"Getting Data from {remote}...")
                self.download_file(remote, local)
            else:
                LOGGER.exception(
                    f"\nFile: >>>{remote}<<< does not exist in remote location.\n"
                    f"Checked in {self._webdav_url}.\nPlease review config."
                )
                self.shut_down_if_missing_file(local)
        except requests.exceptions.Timeout:  
            LOGGER.warning(f"Cannot connect to {self._domain}.\nConnection timed out.")
            self.shut_down_if_missing_file(local)
        except Exception as e:
            LOGGER.error(f"An unexpected error occured when attempting to connect to nc. Error: {e}")

    def push_file(self, file: Path, force:bool = True) -> None:
        """Push File to remote (Update or Upload).

        Args:
            file (Path): Path to local file for upload
            force (bool): If any existign files should be overwritten, default is True
        """
        try:
            if force:
                self.upload_file(get_path(file.name), "/".join((self.remote_dir, file.name)), overwrite=True)
            else:
                self.upload_file(get_path(file.name), "/".join((self.remote_dir, file.name)), overwrite=False)
            LOGGER.info(f"Successfully pushed {file.name} to remote directory.")
        except Exception as e:
            LOGGER.error(f"Failed to upload fail {file.name} to remote with error: {e}")
