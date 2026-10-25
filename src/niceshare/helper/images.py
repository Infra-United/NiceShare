"""Module for handling / caching images."""
import base64
from contextlib import suppress
from io import BytesIO
from os import mkdir
from pathlib import Path

import httpx
import qrcode
from nicegui import app, nicegui, ui
from nicegui.events import UploadEventArguments
from PIL import Image, UnidentifiedImageError
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from slugify import slugify
from starlette.requests import ClientDisconnect

from niceshare.cli import ARGS
from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.ui.helper.validators import IMG_URL_REGEX


def make_thumbnail(path: Path, size: int = 600) -> None:
    """Converts image file to desired resultion for Thumbnail usage.

    NOTE: It currently overwrites the original file 

    Args:
        path (Path): Filepath to the original file
        size (int): Size (size x size) of the image, default 600
    
    """
    if path.is_file():
        image = Image.open(path)
        image.thumbnail((size, size))
        image.save(path)

def match_img_url(to_test: str) -> dict | None:
    """Extracts components from an image url.

    Args:
        to_test (str): Image url to extract components from
    
    Returns:
        dict | None: Dicitinary with url components
    
    """
    try:
        return IMG_URL_REGEX.search(to_test).groupdict()
    except AttributeError:
        return None

def _construct_img_url(subfolder: str, filename: str, file_extension:str, domain: bool) -> str:
    """Constructs an image url for accessing it.
    
    Slugifys the input to handle special characters.

    Args:
        subfolder (str): Subfolder in the images/ folder 
        filename (str): The name of the file (without extension)
        file_extension(str): The file extension (eg. .png)
        domain: (bool): If the web domain should be used

    """
    if domain:
        return f"{settings.domain}/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"
    else:
        return f"/images/{slugify(subfolder)}/{slugify(filename)}.{file_extension}"


def _construct_img_path(subfolder: str, filename: str, file_extension: str) -> Path:
    """Constructs a local Filepath for the image.

    Slugifys the input to handle special characters.

    Args:
        subfolder (str): Subfolder in the images/ folder 
        filename (str): The name of the file (without extension)
        file_extension(str): The file extension (eg. .png)
    """
    return get_path(f"{slugify(subfolder)}/{slugify(filename)}.{file_extension}", "images")


async def upload_img(warehouse_name:str, event: UploadEventArguments, data:dict) -> None:
    """Uploads an image to the site.

    Upload the new image, remove the old one, register the file.

    Args:
        warehouse_name (str): Warehouse name to be used in the file name
        event (UploadEventArguments): #TODO Unused, remove or implemend
        data (dict): Data dict to be updated 
    
    """
    try:
        file_extension = event.file.name.split(".")[-1]
        filename = data[settings.columns['object']]
        path = _construct_img_path(warehouse_name, filename, file_extension)
        img_url = _construct_img_url(warehouse_name, filename, file_extension, domain=False)
        path.unlink(missing_ok=True)
        app.remove_route(img_url)
        await event.file.save(path)
        make_thumbnail(path)
        app.add_static_file(local_file=path, url_path=img_url)
        data[settings.columns["image"]] = _construct_img_url(warehouse_name, filename, file_extension, domain=True)
        ui.notify("Upload successful.")
    except ClientDisconnect:
        ui.notify("Connection failed, please retry uploading the image.")

async def delete_img(data: dict) -> None:
    """Removes images from the site and local filesystem.

    Args:
        data (dict): Data dict to be updated
    
    """
    url_dict: dict|None = match_img_url(data[settings.columns["image"]])
    if url_dict and url_dict.get("domain") == settings.domain:
        with suppress(FileNotFoundError):
            get_path(url_dict["path"]).unlink(missing_ok=True)
            app.remove_route(url_dict.get("path"))
            ui.notify(f"Deleted {url_dict["path"]}")
    data[settings.columns["image"]] = ""

async def cache_image(url_dict: dict[str, str], subfolder:str, filename: str, thumbnail_size:int = 600) -> (str, str, dict, bool):
    """Caches images from external URL for local storage.

    Images from external server are cached locally for faster loading and fewer requests.

    Args:
        url_dict (dict[str, str]): Url dict of the file 
        subfolder (str): The subfolder in images/
        filename (str): The name of the file (With suffix)
        thumbnail_size (int): The desired size (default 600)

    Returns:
        (str, str, dict, bool): Same as the input but from the local system 

    """
    path = _construct_img_path(subfolder, filename, url_dict["ext"])
    if (not path.is_file() and url_dict["domain"] != settings.domain) or ARGS.images:
        try:
            response = await nicegui.run.io_bound(httpx.get,url_dict["url"], timeout=5)
            if response.status_code == 200 and response.headers["content-type"].startswith("image"):
                image = Image.open(BytesIO(response.content))
                if not get_path(subfolder, "images").is_dir():
                    Path.mkdir(get_path(subfolder, "images"))
                image.save(path)
                make_thumbnail(path, thumbnail_size)
                LOGGER.info(f"Successfully downloaded image from {url_dict['url']} and saved to {path}")
        except httpx.TimeoutException, httpx.ReadTimeout, UnidentifiedImageError, ValueError, OSError:
            LOGGER.exception(f"Could not download image from {url_dict['url']} and save it to {path}", exc_info=True)
            return None
    img_url = _construct_img_url(subfolder, filename, url_dict["ext"], domain=False)
    try:
        app.add_static_file(local_file=path, url_path=img_url)
    except FileNotFoundError:
        return url_dict.get("url")
    return _construct_img_url(subfolder, filename, url_dict["ext"], domain=True)

async def cache_base64_img(src:str, subfolder:str, filename:str, thumbnail_size:int = 600) -> str | (str, str, dict, bool):
    """Caches base64 images into regular binary file.

    Args:
        src (str): The source image (base64 text)
        subfolder (str): The subfolder in images/
        filename (str): The name of the file (With suffix)
        thumbnail_size (int): The desired size (default 600)
    
    Returns:
        (str, str, dict, bool): Same as the input but from the local system or the original base64 string if failed

    """
    split = src.split(";base64,")
    base = split[-1]
    ext = split[0].split("/")[-1]
    path = _construct_img_path(subfolder, filename, ext)
    if not path.is_file() or ARGS.images:
        try:
            Image.open(BytesIO(base64.b64decode(base))).save(path)
            make_thumbnail(path, thumbnail_size)
            LOGGER.info(f"Successfully converted image from {split[-1]} and saved to {path}.")
        except OSError: 
            LOGGER.exception(f"Could not convert image from {split[-1]} and save it to {path}", exc_info=True)
            return src
    img_url = _construct_img_url(subfolder, filename, ext, domain=False)
    try:
        app.add_static_file(local_file=path, url_path=img_url)
    except FileNotFoundError:
        return src
    return _construct_img_url(subfolder, filename, ext, domain=True)

def generate_qrcode(data: str, subfolder:str, filename:str) -> (Image, str):
    """Generate qr code.

    Genereates a QR-Code with high error correction and the website logo.

    Args:
        data (str): Data that it should contain
        subfolder (str): Subfolder in /images to store the code in
        filename (str): The name of the qr-code image
    
    Returns:
        (Image, str): The image object and the string of the path

    """
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(), embedded_image_path=get_path(settings.logo))
    path = _construct_img_path(subfolder, filename, "png")
    img.save(path)
    return img, path