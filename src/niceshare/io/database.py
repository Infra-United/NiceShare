import re
from typing import Literal

import duckdb
from polars import DataFrame

from niceshare.helper.config import settings
from niceshare.helper.logger import LOGGER
from niceshare.helper.paths import get_path
from niceshare.io.warehouse import Warehouse


class DB:
    Inventory_DB = get_path(settings.data_filename).with_suffix(".duckdb")
    Request_DB = get_path(settings.requests["filename"]).with_suffix(".duckdb")

    @staticmethod
    def _validate_table_name(name: str) -> str:
        """Validate and quote table identifier to prevent SQL injection (CWE-89).

        Ensures that table names consist only of safe alphanumeric characters and
        underscores, and returns a safely double-quoted SQL identifier.
        """
        if not name or not isinstance(name, str):
            raise ValueError(f"Table name must be a non-empty string, got: {name!r}")
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Table name cannot be empty or whitespace only")
        if not re.match(r"^[a-zA-Z0-9_]+$", cleaned):
            raise ValueError(f"Invalid table identifier '{name}': only alphanumeric characters and underscores are allowed")
        return f'"{cleaned}"'

    @classmethod
    def save(cls, name: str, df: DataFrame, db: Literal["inventory", "request"]):
        safe_name = cls._validate_table_name(name)
        file = cls.Inventory_DB if db == "inventory" else cls.Request_DB
        with duckdb.connect(file, read_only=False) as con:
            con.sql(f"DROP TABLE IF EXISTS {safe_name}")  # nosec B608 - validated by _validate_table_name
            con.sql(f"CREATE TABLE {safe_name} AS SELECT * FROM df")  # nosec B608 - validated by _validate_table_name

    @classmethod
    def load(cls, name: str, db: Literal["inventory", "request"]) -> Warehouse:
        LOGGER.debug(f"Trying to load {name} from database {cls.Inventory_DB.name}...")
        safe_name = cls._validate_table_name(name)
        file = cls.Inventory_DB if db == "inventory" else cls.Request_DB
        with duckdb.connect(database=file, read_only=True) as con:
            df = con.query(f"SELECT * FROM {safe_name}").pl()  # nosec B608 - validated by _validate_table_name
            return Warehouse(name, df)
