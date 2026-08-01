"""
AIMS ERP
Inventory Constants

Used by:
- Inventory Transactions
- Warehouse
- Media Rolls
- Packages
- Dispatch
- Reporting
"""


# ==========================================================
# Inventory Transaction Types
# ==========================================================

class InventoryTransactionType:

    RECEIPT = "RECEIPT"

    ISSUE = "ISSUE"

    TRANSFER = "TRANSFER"

    RETURN = "RETURN"

    ADJUSTMENT = "ADJUSTMENT"

    DAMAGE = "DAMAGE"

    CONSUMPTION = "CONSUMPTION"

    LOST = "LOST"

    FOUND = "FOUND"


# ==========================================================
# Inventory Direction
# ==========================================================

class InventoryDirection:

    IN = "IN"

    OUT = "OUT"

    INTERNAL = "INTERNAL"


# ==========================================================
# Inventory Source
# ==========================================================

class InventorySource:

    PURCHASE = "PURCHASE"

    PRODUCTION = "PRODUCTION"

    WAREHOUSE = "WAREHOUSE"

    DISPATCH = "DISPATCH"

    EXECUTION = "EXECUTION"

    RETURN = "RETURN"


# ==========================================================
# Warehouse Location Types
# ==========================================================

class WarehouseLocationType:

    RECEIVING = "RECEIVING"

    STORAGE = "STORAGE"

    PRINTING = "PRINTING"

    PACKAGING = "PACKAGING"

    DISPATCH = "DISPATCH"

    QUARANTINE = "QUARANTINE"

    SCRAP = "SCRAP"


# ==========================================================
# Inventory Adjustment Reasons
# ==========================================================

class AdjustmentReason:

    PHYSICAL_COUNT = "PHYSICAL_COUNT"

    DAMAGE = "DAMAGE"

    LOST = "LOST"

    FOUND = "FOUND"

    SYSTEM_CORRECTION = "SYSTEM_CORRECTION"

    QUALITY_REJECTION = "QUALITY_REJECTION"

    RETURN_FROM_SITE = "RETURN_FROM_SITE"
