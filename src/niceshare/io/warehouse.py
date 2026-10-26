"""Warehouse Data Module."""
from dataclasses import dataclass
from typing import override

import polars as pl
from polars import DataFrame
from slugify import slugify

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.io.cache import Cache
from niceshare.io.wiki import MenuItem

COLUMNS = settings.columns
WAREHOUSE_ROOT = slugify(settings.warehouse["label"])

@dataclass
class Warehouse(MenuItem):
    """Warehouse Menu Item."""
    name: str
    inventory: DataFrame

    @override
    @property
    def children(self) -> list[str]:
        """Warehouse categories Getter.

        Returns:
            list[str]: List of categorie names
        """
        return self.categories

    @override
    @property
    def routes(self) -> dict[str, str]:
        """Getter for warehouse category path dict.

        Returns:
            dict[str, str]: Dict of category name and path 

        """
        routes: dict[str, str] = {}
        for category in self.categories:
            routes.update({category: f"/{WAREHOUSE_ROOT}/{slugify(self.name)}/{slugify(category)}"})
        return routes

    @classmethod
    def create(cls, name: str, df: DataFrame) -> Warehouse:
        """Creates warehouse.

        Args:
            name (str): Name of the warehouse
            df (DataFrame): Df to save warehouse values to
        
        Returns:
            Warehouse: The created warehouse

        """
        LOGGER.debug(f"Creating warehouse {name}...")
        # with pl.Config(tbl_cols=-1):
        #   print(df.filter(pl.col(COLUMNS["object"]).str.contains("regal")))
        df = df.with_columns(
            [
                pl.col(COLUMNS["count"]).cast(pl.Int64, strict=False),
                pl.col(COLUMNS["weight"]).cast(pl.Float64, strict=False),
                pl.col(COLUMNS["count"]).alias(COLUMNS["total"]).cast(pl.Int64, strict=False),
            ]
        )
        if COLUMNS["total_weight"] not in df.COLUMNS:
            df.insert_column(1, (pl.col(COLUMNS["count"]) * pl.col(COLUMNS["weight"])).alias(COLUMNS["total_weight"]))
        else:
            df.with_columns(pl.col(COLUMNS["count"]) * pl.col(COLUMNS["weight"]).alias(COLUMNS["total_weight"]))
        warehouse = cls(name=name, inventory=df.select(list(COLUMNS.values())).with_row_index())
        warehouse.inventory.insert_column(0, (pl.lit(name)).alias(settings.warehouse["label"]))
        LOGGER.info(f"Successfully created warehouse {name}")
        return warehouse

    @property
    def categories(self) -> list[str]:
        """Categorie name getter.

        Returns:
            list[str]: List of categorie names
        """
        c = [settings.warehouse["selection"], self.name]
        try:
            c.extend(sorted(self.inventory[settings.columns["category"]].unique()))
        except (AttributeError, TypeError) as e:
            raise AttributeError from e(
                "It seems like you have used a category that is not sortable."
                "\nPlease review the categories used in the category column of the inventory file."
                "\nCheck for empty cells, and stuff like numbers, non-ascii-characters, etc."
            )
        return c

    def selected(self) -> DataFrame:
        """Getter for all selected elements of the warehouse.

        Returns:
            DataFrame: Df with all selected elements

        """
        return self.inventory.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name)))

    # TODO Maybe remove async and await, why are they needet?
    async def total_weight(self) -> int:
        """Getter for the total weight.

        Returns:
            int: The total weight

        """
        df = await self.get_final()
        return df.select(COLUMNS["total_weight"]).sum().cast(pl.Int64).item()

    # TODO Maybe remove async and await, why are they needet?
    async def get_final(self) -> DataFrame:
        """#TODO.

        Returns:
            DataFrame: The final Inventory values
            
        """
        df = self.inventory
        for row_idx, value in Cache.amounts(self.name).items():
            df[int(row_idx), COLUMNS["count"]] = value
        return (
            df.filter(pl.arange(0, self.inventory.height).is_in(Cache.selected(self.name))).drop("index")
        ).with_columns((pl.col(COLUMNS["count"]) * pl.col(COLUMNS["weight"])).alias(COLUMNS["total_weight"]))