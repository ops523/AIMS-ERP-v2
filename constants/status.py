"""
AIMS ERP
Status Constants

Single source of truth for all business object statuses.
"""


# ============================================================
# Campaign
# ============================================================

class CampaignStatus:

    DRAFT = "DRAFT"

    PLANNED = "PLANNED"

    ACTIVE = "ACTIVE"

    PAUSED = "PAUSED"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


# ============================================================
# Production Batch
# ============================================================

class ProductionBatchStatus:

    DRAFT = "DRAFT"

    PLANNED = "PLANNED"

    IN_PROGRESS = "IN_PROGRESS"

    ON_HOLD = "ON_HOLD"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


# ============================================================
# Media Roll
# ============================================================

class MediaRollStatus:

    RECEIVED = "RECEIVED"

    AVAILABLE = "AVAILABLE"

    RESERVED = "RESERVED"

    ALLOCATED = "ALLOCATED"

    PRINTING = "PRINTING"

    PRINTED = "PRINTED"

    PARTIALLY_USED = "PARTIALLY_USED"

    CONSUMED = "CONSUMED"

    RETURNED = "RETURNED"

    DAMAGED = "DAMAGED"

    LOST = "LOST"


# ============================================================
# Package
# ============================================================

class PackageStatus:

    CREATED = "CREATED"

    READY = "READY"

    DISPATCHED = "DISPATCHED"

    DELIVERED = "DELIVERED"

    RETURNED = "RETURNED"


# ============================================================
# Dispatch
# ============================================================

class DispatchStatus:

    CREATED = "CREATED"

    LOADING = "LOADING"

    IN_TRANSIT = "IN_TRANSIT"

    DELIVERED = "DELIVERED"

    FAILED = "FAILED"

    RETURNED = "RETURNED"


# ============================================================
# Warehouse
# ============================================================

class WarehouseStatus:

    ACTIVE = "ACTIVE"

    INACTIVE = "INACTIVE"

    BLOCKED = "BLOCKED"


# ============================================================
# Inventory Transaction
# ============================================================

class InventoryTransactionStatus:

    PENDING = "PENDING"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"
