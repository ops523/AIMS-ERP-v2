from __future__ import annotations

from constants.roles import (
    ADMIN,
    OPERATIONS,
    WAREHOUSE,
    PRINTER,
    DISPATCH,
    VIEWER,
)


# =========================================================
# PERMISSIONS
# =========================================================

CAMPAIGNS_VIEW = "campaigns.view"
CAMPAIGNS_MANAGE = "campaigns.manage"

MEDIA_ROLLS_VIEW = "media_rolls.view"
MEDIA_ROLLS_MANAGE = "media_rolls.manage"

INVENTORY_VIEW = "inventory.view"
INVENTORY_MANAGE = "inventory.manage"

PRODUCTION_VIEW = "production.view"
PRODUCTION_MANAGE = "production.manage"

PACKAGING_VIEW = "packaging.view"
PACKAGING_MANAGE = "packaging.manage"

DISPATCH_VIEW = "dispatch.view"
DISPATCH_MANAGE = "dispatch.manage"

USERS_VIEW = "users.view"
USERS_MANAGE = "users.manage"

REPORTS_VIEW = "reports.view"


# =========================================================
# ROLE PERMISSIONS
# =========================================================

ROLE_PERMISSIONS = {

    ADMIN: {
        CAMPAIGNS_VIEW,
        CAMPAIGNS_MANAGE,
        MEDIA_ROLLS_VIEW,
        MEDIA_ROLLS_MANAGE,
        INVENTORY_VIEW,
        INVENTORY_MANAGE,
        PRODUCTION_VIEW,
        PRODUCTION_MANAGE,
        PACKAGING_VIEW,
        PACKAGING_MANAGE,
        DISPATCH_VIEW,
        DISPATCH_MANAGE,
        USERS_VIEW,
        USERS_MANAGE,
        REPORTS_VIEW,
    },

    OPERATIONS: {
        CAMPAIGNS_VIEW,
        CAMPAIGNS_MANAGE,
        MEDIA_ROLLS_VIEW,
        MEDIA_ROLLS_MANAGE,
        PRODUCTION_VIEW,
        PRODUCTION_MANAGE,
        REPORTS_VIEW,
    },

    WAREHOUSE: {
        MEDIA_ROLLS_VIEW,
        MEDIA_ROLLS_MANAGE,
        INVENTORY_VIEW,
        INVENTORY_MANAGE,
    },

    PRINTER: {
        MEDIA_ROLLS_VIEW,
        PRODUCTION_VIEW,
        PRODUCTION_MANAGE,
    },

    DISPATCH: {
        PACKAGING_VIEW,
        PACKAGING_MANAGE,
        DISPATCH_VIEW,
        DISPATCH_MANAGE,
        REPORTS_VIEW,
    },

    VIEWER: {
        CAMPAIGNS_VIEW,
        MEDIA_ROLLS_VIEW,
        INVENTORY_VIEW,
        PRODUCTION_VIEW,
        PACKAGING_VIEW,
        DISPATCH_VIEW,
        REPORTS_VIEW,
    },
}


# =========================================================
# PERMISSION CHECK
# =========================================================

def has_permission(
    role: str | None,
    permission: str,
) -> bool:

    if not role:
        return False

    permissions = ROLE_PERMISSIONS.get(
        role,
        set(),
    )

    return permission in permissions


# =========================================================
# ROLE CHECK
# =========================================================

def has_role(
    role: str | None,
    expected_role: str,
) -> bool:

    return role == expected_role


# =========================================================
# MULTIPLE ROLE CHECK
# =========================================================

def has_any_role(
    role: str | None,
    roles: set[str] | list[str] | tuple[str, ...],
) -> bool:

    if not role:
        return False

    return role in roles


# =========================================================
# PRINTER SCOPE
# =========================================================

def can_access_printer(
    role: str | None,
    user_printer_id: int | None,
    requested_printer_id: int | None,
) -> bool:

    # -----------------------------------------------------
    # Admin can access all printers
    # -----------------------------------------------------

    if role == ADMIN:
        return True

    # -----------------------------------------------------
    # Printer users are restricted to their own printer
    # -----------------------------------------------------

    if role == PRINTER:

        if user_printer_id is None:
            return False

        return (
            requested_printer_id
            == user_printer_id
        )

    # -----------------------------------------------------
    # Non-printer roles with printer-level access
    # -----------------------------------------------------

    return True


# =========================================================
# ASSERTION HELPERS
# =========================================================

def require_permission(
    role: str | None,
    permission: str,
) -> None:

    if not has_permission(
        role,
        permission,
    ):

        raise PermissionError(
            f"Role '{role}' does not have "
            f"permission '{permission}'."
        )


def require_printer_access(
    role: str | None,
    user_printer_id: int | None,
    requested_printer_id: int | None,
) -> None:

    if not can_access_printer(
        role=role,
        user_printer_id=user_printer_id,
        requested_printer_id=requested_printer_id,
    ):

        raise PermissionError(
            "You are not authorized to access "
            "this printer's records."
        )
