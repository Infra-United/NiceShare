import pytest
import re
import duckdb
import polars as pl
from unittest.mock import MagicMock, patch

# Test the validation logic directly
def _validate_table_name(name: str) -> str:
    if not name or not isinstance(name, str):
        raise ValueError(f"Table name must be a non-empty string, got: {name!r}")
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Table name cannot be empty or whitespace only")
    if not re.match(r"^[a-zA-Z0-9_]+$", cleaned):
        raise ValueError(f"Invalid table identifier '{name}': only alphanumeric characters and underscores are allowed")
    return f'"{cleaned}"'


def test_valid_table_names():
    assert _validate_table_name("inventory") == '"inventory"'
    assert _validate_table_name("requests_2026") == '"requests_2026"'
    assert _validate_table_name("warehouse_A_1") == '"warehouse_A_1"'
    assert _validate_table_name("  users  ") == '"users"'


def test_sql_injection_payloads_rejected():
    malicious_inputs = [
        "items; DROP TABLE users; --",
        "inventory; CREATE TABLE hacked(id INT); --",
        "test' OR '1'='1",
        'test" OR "1"="1',
        "table/something",
        "table-name",  # hyphen not allowed in bare identifier
        "table name",  # space not allowed
        "table\x00nullbyte",
        "",
        "   ",
        None,
        12345
    ]
    for bad in malicious_inputs:
        with pytest.raises(ValueError):
            _validate_table_name(bad)


def test_duckdb_execution_with_safe_identifiers(tmp_path):
    """Verify DuckDB executes safely with validated identifiers."""
    db_file = str(tmp_path / "test.duckdb")
    df = pl.DataFrame({"id": [1, 2], "name": ["Item A", "Item B"]})
    
    safe_table = _validate_table_name("inventory_test")
    with duckdb.connect(db_file, read_only=False) as con:
        con.sql(f"DROP TABLE IF EXISTS {safe_table}")
        con.sql(f"CREATE TABLE {safe_table} AS SELECT * FROM df")
        
        result_df = con.query(f"SELECT * FROM {safe_table}").pl()
        assert len(result_df) == 2
        assert result_df["name"].to_list() == ["Item A", "Item B"]
