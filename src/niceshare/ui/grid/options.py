"""Options for Gird Styling and display."""
from niceshare.ui.grid.columns import col_defs, default_col_defs


def options(cart: bool, admin: bool) -> dict:
    """Geberates AgGrid options based on user role/privilages and cart mode.
    
    Args:
        cart (bool): Whether in cart mode
        admin (bool): If the user is admin
    
    Returns.
        dict: Dict of AgGrid configuration options 
    
    """
    return {
        "selectionColumnDef": {"hide": cart, "maxWidth": 35, "sortable": True},
        "columnDefs": col_defs(cart, admin),
        "defaultColDef": default_col_defs(),
        "alwaysMultiSort": True,
        "rowSelection": {
            "mode": "multiRow",
            "selectAll": "filtered",
            "checkboxes": True,
            "headerCheckbox": True,
            ":isRowSelectable": "(r) => r.isRowPinned",
        }
        if not cart and not admin
        else "",
        "autoSizePadding": 1,
        "autoSizeStrategy": {
            "type": "fitCellContents",
        },
        "suppressRowHoverHighlight": cart,
        "undoRedoCellEditing": True,
        "undoRedoCellEditingLimit": 20,
        "readOnlyEdit": not admin,
        "invalidEditValueMode": "block" if not admin else "",
        "suppressCellFocus": not admin,
        "enterNavigatesVerticallyAfterEdit": True,
        "singleClickEdit": True,
        "stopEditingWhenCellsLoseFocus": True,
        ":getRowId": "(p) => p.data.index.toString()",
    }
