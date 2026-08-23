from __future__ import annotations

import pytest

from models.production_batch import ProductionBatch
from models.production_item import ProductionItem
from models.production_allocation import ProductionAllocation
from models.printing_session import PrintingSession

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)

from services.production_allocation_service import (
    ProductionAllocationService,
)


# ============================================================
# Helpers
# ============================================================


def _get_session_factory():
    """
    Reuse the test DB/session helpers already present in the
    existing media-roll tests.
    """
    from tests.test_media_roll_inventory_integrity import (
        create_test_db,
    )

    return create_test_db


def _get_models():
    """
    Import the application models used by the test environment.
    """
    from models.campaign_artwork import CampaignArtwork
    from models.campaign import Campaign
    from models.printer import Printer

    return Campaign, CampaignArtwork, Printer


def _create_printer(db):
    """
    Create the minimum Printer record required by ProductionBatch.
    """

    from models.printer import Printer

    printer = Printer(
        printer_code="PACK9B-TEST-PRINTER",
        printer_name="PACK9B-TEST-PRINTER",
        is_active=True,
    )

    db.add(printer)
    db.flush()

    return printer

def _create_campaign(db):
    """
    Create a minimal campaign required by ProductionBatch tests.
    """

    from datetime import date
    from models.campaign import Campaign

    campaign = Campaign(
        campaign_code="PACK9B-TEST-CAMPAIGN",
        client_name="PACK9B TEST CLIENT",
        brand_name="PACK9B TEST BRAND",
        campaign_name="PACK9B TEST CAMPAIGN",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    db.add(campaign)
    db.flush()

    return campaign

def _create_artwork(
    db,
    campaign_version=None,
    sqft=100.0,
):
    """
    Create a minimal CampaignArtwork fixture.

    CampaignArtwork belongs to CampaignVersion,
    not directly to Campaign.
    """

    from models.campaign_artwork import CampaignArtwork

    if campaign_version is None:
        campaign = _create_campaign(db)

        from models.campaign_version import CampaignVersion

        campaign_version = CampaignVersion(
            campaign_id=campaign.id,
            version_no=1,
            version_name="V1",
            import_batch=f"PACK9B-{uuid.uuid4().hex[:8]}",
            total_locations=1,
            total_walls=1,
            total_sqft=sqft,
        )

        db.add(campaign_version)
        db.flush()

    artwork = CampaignArtwork(
        campaign_version_id=campaign_version.id,
        artwork_code=f"PACK9B-ART-{sqft}",
        artwork_name="PACK9B TEST ARTWORK",
        file_name="pack9b-test.jpg",
        width_ft=10.0,
        height_ft=sqft / 10.0,
        artwork_sqft=sqft,
        assigned_walls=1,
    )

    db.add(artwork)
    db.flush()

    return artwork


def _create_batch(
    db,
    printer,
    batch_number="PACK9B-001",
    status="PLANNED",
):
    batch = ProductionBatch(
        batch_number=batch_number,
        printer_id=printer.id,
        status=status,
    )

    db.add(batch)
    db.flush()

    return batch


def _create_item(
    db,
    batch,
    artwork,
    planned_sqft=100.0,
    printed_sqft=0.0,
    wastage_sqft=0.0,
    status="PENDING",
):
    item = ProductionItem(
        production_batch_id=batch.id,
        campaign_artwork_id=artwork.id,
        planned_sqft=planned_sqft,
        printed_sqft=printed_sqft,
        wastage_sqft=wastage_sqft,
        status=status,
    )

    db.add(item)
    db.flush()

    return item


# ============================================================
# Batch Core Integrity
# ============================================================


def test_production_batch_can_be_created():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    assert batch.id is not None
    assert batch.printer_id == printer.id
    assert batch.status == "PLANNED"

    db.close()


def test_production_batch_is_linked_to_printer():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    db.refresh(batch)

    assert batch.printer is not None
    assert batch.printer.id == printer.id

    db.close()


def test_production_batch_number_is_unique():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    _create_batch(
        db=db,
        printer=printer,
        batch_number="PACK9B-UNIQUE",
    )

    db.commit()

    duplicate = ProductionBatch(
        batch_number="PACK9B-UNIQUE",
        printer_id=printer.id,
        status="PLANNED",
    )

    db.add(duplicate)

    with pytest.raises(Exception):
        db.commit()

    db.rollback()
    db.close()


# ============================================================
# Production Item Integrity
# ============================================================


def test_production_item_is_linked_to_batch():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)
    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=250.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=250.0,
    )

    db.refresh(batch)

    assert item.production_batch_id == batch.id
    assert item in batch.production_items

    db.close()


def test_production_item_is_linked_to_campaign_artwork():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=150.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=150.0,
    )

    assert item.campaign_artwork_id == artwork.id
    assert item.campaign_artwork.id == artwork.id

    db.close()


def test_batch_total_planned_sqft_is_calculated():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    campaign = _create_campaign(db)

    artwork1 = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    artwork2 = _create_artwork(
        db,
        campaign=campaign,
        sqft=250.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork1,
        planned_sqft=100.0,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork2,
        planned_sqft=250.0,
    )

    db.refresh(batch)

    assert batch.total_planned_sqft == pytest.approx(350.0)

    db.close()


def test_batch_total_printed_sqft_is_calculated():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork1 = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    artwork2 = _create_artwork(
        db,
        campaign=campaign,
        sqft=200.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork1,
        planned_sqft=100.0,
        printed_sqft=50.0,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork2,
        planned_sqft=200.0,
        printed_sqft=125.0,
    )

    db.refresh(batch)

    assert batch.total_printed_sqft == pytest.approx(175.0)

    db.close()


def test_batch_total_wastage_sqft_is_calculated():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork1 = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    artwork2 = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork1,
        planned_sqft=100.0,
        wastage_sqft=10.0,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork2,
        planned_sqft=100.0,
        wastage_sqft=15.0,
    )

    db.refresh(batch)

    assert batch.total_wastage_sqft == pytest.approx(25.0)

    db.close()


def test_batch_completion_percentage_is_calculated():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=200.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=200.0,
        printed_sqft=50.0,
    )

    db.refresh(batch)

    assert batch.completion_percentage == pytest.approx(25.0)

    db.close()


def test_zero_planned_sqft_has_zero_completion_percentage():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    assert batch.total_planned_sqft == 0
    assert batch.completion_percentage == 0

    db.close()


# ============================================================
# Production Allocation Integrity
# ============================================================


def test_production_allocation_can_be_created():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=100.0,
    )

    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        production_batch_id=batch.id,
        allocated_sqft=100.0,
        printed_sqft=0.0,
        wastage_sqft=0.0,
        balance_sqft=100.0,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.flush()

    assert allocation.id is not None
    assert allocation.production_batch_id == batch.id
    assert allocation.production_item_id == item.id
    assert allocation.campaign_artwork_id == artwork.id

    db.close()


def test_production_allocation_repository_returns_batch_allocations():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=100.0,
    )

    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        production_batch_id=batch.id,
        allocated_sqft=100.0,
        printed_sqft=0.0,
        wastage_sqft=0.0,
        balance_sqft=100.0,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.flush()

    results = ProductionAllocationRepository.get_by_batch(
        db,
        batch.id,
    )

    assert len(results) == 1
    assert results[0].id == allocation.id

    db.close()


def test_allocation_service_creates_allocation():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=batch,
        artwork=artwork,
        required_sqft=100.0,
    )

    assert allocation.id is not None
    assert allocation.production_batch_id == batch.id
    assert allocation.campaign_artwork_id == artwork.id
    assert allocation.allocated_sqft == pytest.approx(100.0)

    db.close()


# ============================================================
# Printing Session Integrity
# ============================================================


def test_printing_session_is_linked_to_batch():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=300.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=300.0,
    )

    session = PrintingSession(
        production_batch_id=batch.id,
        printer_id=printer.id,
        session_number=1,
        planned_sqft=300.0,
        printed_sqft=0.0,
        wastage_sqft=0.0,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    db.refresh(batch)

    assert session.production_batch_id == batch.id
    assert session in batch.printing_sessions

    db.close()


def test_printing_session_planned_sqft_matches_batch():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=400.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=400.0,
    )

    session = PrintingSession(
        production_batch_id=batch.id,
        printer_id=printer.id,
        session_number=1,
        planned_sqft=batch.total_planned_sqft,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    assert session.planned_sqft == pytest.approx(400.0)

    db.close()


def test_printing_session_status_defaults_to_in_progress():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    session = PrintingSession(
        production_batch_id=batch.id,
        printer_id=printer.id,
    )

    db.add(session)
    db.flush()

    assert session.status == "IN_PROGRESS"

    db.close()


# ============================================================
# Persistence Integrity
# ============================================================


def test_batch_items_and_allocations_survive_refresh():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=150.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=150.0,
    )

    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        production_batch_id=batch.id,
        allocated_sqft=150.0,
        balance_sqft=150.0,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.commit()

    db.expire_all()

    loaded_batch = (
        db.query(ProductionBatch)
        .filter(
            ProductionBatch.id == batch.id
        )
        .one()
    )

    assert len(loaded_batch.production_items) == 1
    assert len(loaded_batch.allocations) == 1

    assert (
        loaded_batch.production_items[0].id
        == item.id
    )

    assert (
        loaded_batch.allocations[0].id
        == allocation.id
    )

    db.close()


def test_multiple_allocations_are_kept_separately():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork1 = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    artwork2 = _create_artwork(
        db,
        campaign=campaign,
        sqft=200.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item1 = _create_item(
        db=db,
        batch=batch,
        artwork=artwork1,
        planned_sqft=100.0,
    )

    item2 = _create_item(
        db=db,
        batch=batch,
        artwork=artwork2,
        planned_sqft=200.0,
    )

    allocation1 = ProductionAllocation(
        production_item_id=item1.id,
        campaign_artwork_id=artwork1.id,
        production_batch_id=batch.id,
        allocated_sqft=100.0,
        balance_sqft=100.0,
        status="ALLOCATED",
    )

    allocation2 = ProductionAllocation(
        production_item_id=item2.id,
        campaign_artwork_id=artwork2.id,
        production_batch_id=batch.id,
        allocated_sqft=200.0,
        balance_sqft=200.0,
        status="ALLOCATED",
    )

    db.add_all(
        [
            allocation1,
            allocation2,
        ]
    )

    db.flush()

    allocations = ProductionAllocationRepository.get_by_batch(
        db,
        batch.id,
    )

    assert len(allocations) == 2

    allocated_total = sum(
        allocation.allocated_sqft
        for allocation in allocations
    )

    assert allocated_total == pytest.approx(300.0)

    db.close()


# ============================================================
# Rollback Integrity
# ============================================================


def test_batch_creation_failure_does_not_persist_partial_batch():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = ProductionBatch(
        batch_number="PACK9B-ROLLBACK",
        printer_id=printer.id,
        status="PLANNED",
    )

    db.add(batch)
    db.flush()

    batch_id = batch.id

    db.rollback()

    result = (
        db.query(ProductionBatch)
        .filter(
            ProductionBatch.id == batch_id
        )
        .first()
    )

    assert result is None

    db.close()


def test_allocation_rollback_does_not_persist():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=100.0,
    )

    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        production_batch_id=batch.id,
        allocated_sqft=100.0,
        balance_sqft=100.0,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.flush()

    allocation_id = allocation.id

    db.rollback()

    result = (
        db.query(ProductionAllocation)
        .filter(
            ProductionAllocation.id == allocation_id
        )
        .first()
    )

    assert result is None

    db.close()


# ============================================================
# Relationship Cascade Integrity
# ============================================================


def test_deleting_batch_removes_production_items():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)
    campaign = _create_campaign(db)

    artwork = _create_artwork(
        db,
        campaign=campaign,
        sqft=100.0,
    )

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    item = _create_item(
        db=db,
        batch=batch,
        artwork=artwork,
        planned_sqft=100.0,
    )

    item_id = item.id
    batch_id = batch.id

    db.delete(batch)
    db.commit()

    assert (
        db.query(ProductionItem)
        .filter(
            ProductionItem.id == item_id
        )
        .first()
        is None
    )

    assert (
        db.query(ProductionBatch)
        .filter(
            ProductionBatch.id == batch_id
        )
        .first()
        is None
    )

    db.close()


def test_deleting_batch_removes_printing_sessions():

    create_test_db = _get_session_factory()
    db = create_test_db()

    printer = _create_printer(db)

    batch = _create_batch(
        db=db,
        printer=printer,
    )

    session = PrintingSession(
        production_batch_id=batch.id,
        printer_id=printer.id,
        session_number=1,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    session_id = session.id

    db.delete(batch)
    db.commit()

    assert (
        db.query(PrintingSession)
        .filter(
            PrintingSession.id == session_id
        )
        .first()
        is None
    )

    db.close()
