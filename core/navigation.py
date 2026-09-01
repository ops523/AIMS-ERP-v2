from __future__ import annotations

from dataclasses import dataclass

from core.authorization import has_permission


@dataclass(frozen=True)
class NavigationItem:
    """
    Definition of a single AIMS ERP navigation item.
    """

    label: str
    page: str
    icon: str
    permission: str


# =========================================================
# NAVIGATION DEFINITIONS
# =========================================================

NAVIGATION_ITEMS: tuple[NavigationItem, ...] = (

    NavigationItem(
        label="Campaign Import Wizard",
        page="pages/campaign_wizard.py",
        icon="📦",
        permission="campaigns.view",
    ),

    NavigationItem(
    label="User Management",
    page="pages/user_management.py",
    icon="👥",
    permission="users.view",
    ),

    NavigationItem(
        label="Inventory Ledger",
        page="pages/inventory_ledger.py",
        icon="📚",
        permission="inventory.view",
    ),

    NavigationItem(
        label="Media Roll Inventory",
        page="pages/media_roll_inventory.py",
        icon="📦",
        permission="media_rolls.view",
    ),

    NavigationItem(
        label="Production Batch Wizard",
        page="pages/production_batch_wizard.py",
        icon="🧾",
        permission="production.manage",
    ),

    NavigationItem(
        label="Production",
        page="pages/production_workspace.py",
        icon="🖨️",
        permission="production.view",
    ),

    NavigationItem(
        label="Receive Media Rolls",
        page="pages/receive_roll.py",
        icon="📥",
        permission="media_rolls.manage",
    ),

    NavigationItem(
        label="Roll Details",
        page="pages/roll_details.py",
        icon="🔎",
        permission="media_rolls.view",
    ),

    NavigationItem(
        label="Roll Inventory",
        page="pages/roll_inventory.py",
        icon="📊",
        permission="inventory.view",
    ),
)


# =========================================================
# AUTHORIZED NAVIGATION
# =========================================================

def get_navigation_for_role(
    role: str | None,
) -> list[NavigationItem]:
    """
    Return navigation items accessible to the supplied role.
    """

    if not role:
        return []

    return [
        item
        for item in NAVIGATION_ITEMS
        if has_permission(
            role,
            item.permission,
        )
    ]
