"""Data Importer for Warehouses and images."""
import polars as pl
from _duckdb import CatalogException, IOException
from polars import DataFrame
from polars.exceptions import NoDataError

from niceshare.helper.config import settings
from niceshare.helper.images import cache_image, match_img_url
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.warehouse import Warehouse


def read_inventory(sheet: str) -> Warehouse:
    """Creates Warehouse from an xlsx (Excel) sheet.

    Handles file formats: xlsx

    Args:
        sheet (str): The Warehouse Data File (Path)
    
    Returns:
        Warehouse: Newly created warehouse object 

    """
    inventory = get_path(settings.data_filename)
    # NOTE: Removed commented out part for now (not implemented file types)
    try:
        df = pl.read_excel(source=inventory.with_suffix(".xlsx"), sheet_name=sheet, engine="openpyxl", drop_empty_cols=False)
        return Warehouse.create(sheet, df)
    except (FileNotFoundError, NoDataError, IOException, CatalogException) as e:
        LOGGER.warning(f"Unable to read {sheet} from {inventory.name}. Full error: {e}", exc_info=True)
        exit(1)


async def handle_images(subfolder: str, df: DataFrame) -> DataFrame:
    """Manually caches linked images to DataFrame based on url.

    Args:
        subfolder (str): Subfolder (Path) to image folder
        df (DataFrame): Df with image paths to be replaced
    
    Returns:
        DataFrame: Returns the df with cached images
    """   
    img_col = settings.columns.get("image")
    obj_col = settings.columns.get("object")
    if img_col and obj_col and img_col in df.columns:
        for idx, (img, file) in enumerate(df[[img_col, obj_col]].rows()):
            if img and (url_dict := match_img_url(img)):
                df[idx, img_col] = await cache_image(url_dict, subfolder, file)
    return df