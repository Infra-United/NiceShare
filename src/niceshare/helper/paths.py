"""Path Enforcment module."""
from pathlib import Path
from typing import Literal

import niceshare

#TODO Move creation rules from main.py here as well
DIRS = ["users", "images", "locales", "lists", "pages"] #Directorys that need to be created

def ensure_directory_structure(warehouse_names: list[str]) -> None:
    """Creates any missing directorys.

    Args:
        warehouse_names (list[str]): List of all warehouse names 
    
    """
    for d in DIRS:
        d = get_path(d)
        if not d.exists():
            Path.mkdir(d)
        if d == "images":
            for w in warehouse_names:
                w_dir = get_path(w, "images")
                if not w_dir.is_dir():
                    Path.mkdir(w_dir)


def get_path(filename: str, subdir: Literal["users", "images", "locales", "lists", "pages"] | None = None) -> Path:
    """Returns a full filepath based on the name (with suffix) and a subdirectory (or none) to search in.

    Args:
        filename (str): The name of the file to return the path from
        subdir (Literal["users", "images", "locales", "lists", "pages"]): Literal options for subfolders to search in

    Returns:
        Path: The requested path 
    
    """
    if subdir is not None:
        return Path(niceshare.__file__).parent.parent.parent.joinpath(f"files/{subdir}/{filename}")
    else:
        return Path(niceshare.__file__).parent.parent.parent.joinpath(f"files/{filename}")