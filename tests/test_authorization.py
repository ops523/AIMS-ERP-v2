import pytest

from constants.roles import (
    ADMIN,
    OPERATIONS,
    WAREHOUSE,
    PRINTER,
    DISPATCH,
    VIEWER,
)

from core.authorization import (
    CAMPAIGNS_MANAGE,
    CAMPAIGNS_VIEW,
    MEDIA_ROLLS_MANAGE,
    MEDIA_ROLLS_VIEW,
    INVENTORY_MANAGE,
    INVENTORY_VIEW,
    PRODUCTION_MANAGE,
    PRODUCTION_VIEW,
    PACKAGING_MANAGE,
    PACKAGING_VIEW,
    DISPATCH_MANAGE,
    DISPATCH_VIEW,
    USERS_MANAGE,
    USERS_VIEW,
    REPORTS_VIEW,
    can_access_printer,
    has_any_role,
    has_permission,
    has_role,
    require_permission,
    require_printer_access,
)


def test_admin_has_all_permissions():

    permissions = [
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
    ]

    for permission in permissions:

        assert has_permission(
            ADMIN,
            permission,
        )


def test_operations_permissions():

    assert has_permission(
        OPERATIONS,
        CAMPAIGNS_VIEW,
    )

    assert has_permission(
        OPERATIONS,
        CAMPAIGNS_MANAGE,
    )

    assert has_permission(
        OPERATIONS,
        PRODUCTION_VIEW,
    )

    assert has_permission(
        OPERATIONS,
        PRODUCTION_MANAGE,
    )

    assert not has_permission(
        OPERATIONS,
        INVENTORY_MANAGE,
    )

    assert not has_permission(
        OPERATIONS,
        USERS_MANAGE,
    )


def test_warehouse_permissions():

    assert has_permission(
        WAREHOUSE,
        MEDIA_ROLLS_VIEW,
    )

    assert has_permission(
        WAREHOUSE,
        MEDIA_ROLLS_MANAGE,
    )

    assert has_permission(
        WAREHOUSE,
        INVENTORY_VIEW,
    )

    assert has_permission(
        WAREHOUSE,
        INVENTORY_MANAGE,
    )

    assert not has_permission(
        WAREHOUSE,
        PRODUCTION_MANAGE,
    )


def test_printer_permissions():

    assert has_permission(
        PRINTER,
        MEDIA_ROLLS_VIEW,
    )

    assert has_permission(
        PRINTER,
        PRODUCTION_VIEW,
    )

    assert has_permission(
        PRINTER,
        PRODUCTION_MANAGE,
    )

    assert not has_permission(
        PRINTER,
        USERS_MANAGE,
    )

    assert not has_permission(
        PRINTER,
        INVENTORY_MANAGE,
    )


def test_dispatch_permissions():

    assert has_permission(
        DISPATCH,
        PACKAGING_VIEW,
    )

    assert has_permission(
        DISPATCH,
        PACKAGING_MANAGE,
    )

    assert has_permission(
        DISPATCH,
        DISPATCH_VIEW,
    )

    assert has_permission(
        DISPATCH,
        DISPATCH_MANAGE,
    )

    assert not has_permission(
        DISPATCH,
        PRODUCTION_MANAGE,
    )


def test_viewer_is_read_only():

    assert has_permission(
        VIEWER,
        CAMPAIGNS_VIEW,
    )

    assert has_permission(
        VIEWER,
        PRODUCTION_VIEW,
    )

    assert has_permission(
        VIEWER,
        REPORTS_VIEW,
    )

    assert not has_permission(
        VIEWER,
        CAMPAIGNS_MANAGE,
    )

    assert not has_permission(
        VIEWER,
        PRODUCTION_MANAGE,
    )

    assert not has_permission(
        VIEWER,
        DISPATCH_MANAGE,
    )


def test_unknown_role_has_no_permissions():

    assert not has_permission(
        "UnknownRole",
        CAMPAIGNS_VIEW,
    )

    assert not has_permission(
        None,
        CAMPAIGNS_VIEW,
    )


def test_role_helpers():

    assert has_role(
        ADMIN,
        ADMIN,
    )

    assert not has_role(
        ADMIN,
        PRINTER,
    )

    assert has_any_role(
        ADMIN,
        {ADMIN, OPERATIONS},
    )

    assert not has_any_role(
        PRINTER,
        {ADMIN, OPERATIONS},
    )


def test_printer_can_access_own_printer():

    assert can_access_printer(
        role=PRINTER,
        user_printer_id=10,
        requested_printer_id=10,
    )


def test_printer_cannot_access_other_printer():

    assert not can_access_printer(
        role=PRINTER,
        user_printer_id=10,
        requested_printer_id=20,
    )


def test_printer_without_assignment_has_no_printer_access():

    assert not can_access_printer(
        role=PRINTER,
        user_printer_id=None,
        requested_printer_id=10,
    )


def test_admin_can_access_any_printer():

    assert can_access_printer(
        role=ADMIN,
        user_printer_id=None,
        requested_printer_id=10,
    )

    assert can_access_printer(
        role=ADMIN,
        user_printer_id=None,
        requested_printer_id=20,
    )


def test_non_printer_roles_can_access_printer_records():

    assert can_access_printer(
        role=OPERATIONS,
        user_printer_id=None,
        requested_printer_id=10,
    )

    assert can_access_printer(
        role=WAREHOUSE,
        user_printer_id=None,
        requested_printer_id=10,
    )


def test_require_permission_allows_authorized_role():

    require_permission(
        ADMIN,
        USERS_MANAGE,
    )


def test_require_permission_rejects_unauthorized_role():

    with pytest.raises(PermissionError):

        require_permission(
            PRINTER,
            USERS_MANAGE,
        )


def test_require_printer_access_allows_own_printer():

    require_printer_access(
        role=PRINTER,
        user_printer_id=10,
        requested_printer_id=10,
    )


def test_require_printer_access_rejects_other_printer():

    with pytest.raises(PermissionError):

        require_printer_access(
            role=PRINTER,
            user_printer_id=10,
            requested_printer_id=20,
        )
