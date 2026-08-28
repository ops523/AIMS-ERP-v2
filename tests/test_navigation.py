from constants.roles import (
    ADMIN,
    OPERATIONS,
    PRINTER,
    WAREHOUSE,
)

from core.navigation import (
    get_navigation_for_role,
)


def _labels(role):
    return {
        item.label
        for item in get_navigation_for_role(role)
    }


def test_admin_gets_all_current_navigation_items():

    labels = _labels(ADMIN)

    assert "Campaign Import Wizard" in labels
    assert "Media Roll Inventory" in labels
    assert "Receive Media Rolls" in labels
    assert "Roll Inventory" in labels
    assert "Inventory Ledger" in labels
    assert "Roll Details" in labels
    assert "Production" in labels
    assert "Production Batch Wizard" in labels


def test_operations_can_access_campaigns_and_production():

    labels = _labels(OPERATIONS)

    assert "Campaign Import Wizard" in labels
    assert "Media Roll Inventory" in labels
    assert "Receive Media Rolls" in labels
    assert "Production" in labels
    assert "Production Batch Wizard" in labels


def test_printer_can_access_production():

    labels = _labels(PRINTER)

    assert "Production" in labels
    assert "Production Batch Wizard" in labels


def test_printer_cannot_access_campaign_import():

    labels = _labels(PRINTER)

    assert "Campaign Import Wizard" not in labels


def test_warehouse_can_access_inventory():

    labels = _labels(WAREHOUSE)

    assert "Media Roll Inventory" in labels
    assert "Receive Media Rolls" in labels
    assert "Roll Inventory" in labels
    assert "Inventory Ledger" in labels


def test_unknown_role_gets_no_navigation():

    assert get_navigation_for_role(
        "Unknown Role"
    ) == []


def test_no_role_gets_no_navigation():

    assert get_navigation_for_role(None) == []
