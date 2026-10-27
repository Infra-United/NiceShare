"""Handler for Inventory and Request Databse (duckdb)."""
from typing import Literal

import duckdb
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.warehouse import Warehouse


class DB:
    """Database Class."""

    # Path constants to the file
    INVENTORY_DB = get_path(settings.data_filename).with_suffix(".duckdb") # Duckdb file for inventory managment
    REQUEST_DB = get_path(settings.requests["filename"]).with_suffix(".duckdb") # Duckdb file for request managment

    @classmethod
    def save(cls, name: str, df: DataFrame, db: Literal["inventory", "request"]) -> None:
        """Save Data to Database.

        Args:
            name (str): Name of the inventory / request 
            df (DataFrame): Pandas Dataframe with warehouse/request data to save
            db (Literal["inventory", "request"]): Storing inventory or request data Option

        #NOTE No Validation / Safeguard happens for preventing request data to be loadet into the inventory db.

        """
        file = cls.INVENTORY_DB if db == "inventory" else cls.REQUEST_DB
        with duckdb.connect(file, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {name}")
            con.sql(f"CREATE TABLE {name} AS SELECT * FROM df") #TODO Possible SQL injection vector through string-based query construction

    @classmethod
    def load_warehouse(cls, name: str, db: Literal["inventory", "request"]) -> Warehouse:
        """Load and construct Warehouse from Database.

        Args:
            name (str): Name of the Warehouse to load
            db (Literal["inventory", "request"]): If the warehouse should be loaded from inventory or request db

        Returns:
            Warehouse: The Warehouse object 

        """
        LOGGER.debug(f"Trying to load {name} from database {cls.INVENTORY_DB.name}...")
        file = cls.INVENTORY_DB if db == "inventory" else cls.REQUEST_DB
        
        if not file.exists():
            LOGGER.error("Database inventory does not exist")
            raise FileNotFoundError
            
        with duckdb.connect(database=file, read_only=True) as con:
            # Creates Polar Dataframe from read-only duckdb database 
            # TODO WHY, why is this so cursed
            df = con.query(f"SELECT * FROM {name}").pl() #Possible SQL injection vector through string-based query construction
            return Warehouse(name, df)

