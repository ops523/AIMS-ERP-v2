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
    section: str


# =========================================================
# NAVIGATION DEFINITIONS
# =========================================================

NAVIGATION_ITEMS: tuple[NavigationItem, ...] = (

    # -----------------------------------------------------
    # CAMPAIGN
    # -----------------------------------------------------

    NavigationItem(
        label="Campaign Import Wizard",
        page="pages/campaign_wizard.py",
        icon="📦",
        permission="campaigns.view",
        section="CAMPAIGN",
    ),

    # -----------------------------------------------------
    # INVENTORY
    # -----------------------------------------------------

    NavigationItem(
        label="Receive Media Rolls",
        page="pages/receive_roll.py",
        icon="📥",
        permission="media_rolls.manage",
        section="INVENTORY",
    ),

    NavigationItem(
        label="Media Roll Inventory",
        page="pages/media_roll_inventory.py",
        icon="📦",
        permission="media_rolls.view",
        section="INVENTORY",
    ),

    NavigationItem(
        label="Inventory Ledger",
        page="pages/inventory_ledger.py",
        icon="📚",
        permission="inventory.view",
        section="INVENTORY",
    ),

    # -----------------------------------------------------
    # PRODUCTION
    # -----------------------------------------------------

    NavigationItem(
        label="Production Batch Wizard",
        page="pages/production_batch_wizard.py",
        icon="🧾",
        permission="production.manage",
        section="PRODUCTION",
    ),

    NavigationItem(
        label="Production",
        page="pages/production_workspace.py",
        icon="🖨️",
        permission="production.view",
        section="PRODUCTION",
    ),

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    NavigationItem(
        label="User Management",
        page="pages/user_management.py",
        icon="👥",
        permission="users.view",
        section="ADMIN",
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

    Items retain the defined section and ordering.
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


# =========================================================
# GROUPED NAVIGATION
# =========================================================

def get_navigation_sections(
    role: str | None,
) -> dict[str, list[NavigationItem]]:
    """
    Return authorized navigation items grouped by section.

    Section order is:

        CAMPAIGN
        INVENTORY
        PRODUCTION
        ADMIN
    """

    authorized_items = get_navigation_for_role(role)

    sections: dict[str, list[NavigationItem]] = {}

    for item in authorized_items:

        if item.section not in sections:
            sections[item.section] = []

        sections[item.section].append(item)

    return sections