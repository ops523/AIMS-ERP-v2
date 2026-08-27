from __future__ import annotations

import inspect

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.campaign import Campaign
from models.campaign_artwork import CampaignArtwork
from models.campaign_version import CampaignVersion
from models.media_roll import MediaRoll
from models.printer import Printer
from models.production_allocation import ProductionAllocation
from models.production_batch import ProductionBatch
from models.production_item import ProductionItem
from models.printing_session import PrintingSession

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)

from services.production_allocation_service import (
    ProductionAllocationService,
)


# ============================================================
# TEST DATABASE
# ============================================================

def _get_session_factory():
    """
    Create a completely isolated in-memory SQLite database.

    The application models are used directly so these tests
    validate the actual Pack 9B ORM structure.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
    )

    Base.metadata.create_all(engine)

    return sessionmaker(
        bind=engine,
        autoflush=True,
        expire_on_commit=False,
    )


# ============================================================
# FIXTURES / HELPERS
# ============================================================

def _create_printer(db):
    """
    Create the minimum Printer record required by ProductionBatch.

    Current Printer model requires printer_code.
    """

    printer = Printer(
        printer_code="PACK9B-PRINTER-001",
        printer_name="PACK9B-TEST-PRINTER",
        is_active=True,
    )

    db.add(printer)
    db.flush()

    return printer


def _create_campaign(db, suffix="001"):
    """
    Create a valid Campaign record.

    Current Campaign model requires:
        campaign_code
        client_name
        brand_name
        campaign_name
        start_date
    """

    from datetime import date

    campaign = Campaign(
        campaign_code=f"PACK9B-CAMPAIGN-{suffix}",
        client_name="PACK9B TEST CLIENT",
        brand_name="PACK9B TEST BRAND",
        campaign_name=f"PACK9B TEST CAMPAIGN {suffix}",
        start_date=date(2026, 1, 1),
    )

    db.add(campaign)
    db.flush()

    return campaign


def _create_campaign_version(
    db,
    campaign,
    suffix="001",
):
    """
    Create the CampaignVersion required by CampaignArtwork.
    """

    version = CampaignVersion(
        campaign_id=campaign.id,
        version_no=1,
        version_name="V1",
        import_batch=f"PACK9B-IMPORT-{suffix}",
        total_locations=1,
        total_walls=1,
        total_sqft=250,
    )

    db.add(version)
    db.flush()

    return version


def _create_artwork(
    db,
    campaign_version,
    sqft=100.0,
    suffix="001",
):
    """
    Create a valid CampaignArtwork.

    CampaignArtwork is linked to CampaignVersion, not directly
    to Campaign.
    """

    artwork = CampaignArtwork(
        campaign_version_id=campaign_version.id,
        artwork_code=f"PACK9B-ART-{suffix}",
        artwork_name=f"PACK9B TEST ARTWORK {suffix}",
        file_name=f"pack9b_test_{suffix}.png",
        width_ft=10.0,
        height_ft=10.0,
        artwork_sqft=sqft,
        assigned_walls=0,
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
    """
    Create a ProductionBatch.
    """

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
):
    """
    Create a ProductionItem linked to both the batch and artwork.
    """

    item = ProductionItem(
        production_batch_id=batch.id,
        campaign_artwork_id=artwork.id,
        planned_sqft=planned_sqft,
        printed_sqft=0,
        wastage_sqft=0,
        status="PENDING",
    )

    db.add(item)
    db.flush()

    return item


def _create_media_roll(
    db,
    suffix="001",
    total_sqft=400.0,
):
    """
    Create a valid MediaRoll.

    The current MediaRoll model requires:
        asset_id
        roll_number
        supplier_id
        manufacturer_id
        product_id
        warehouse_id
        ordered_length_m
        actual_length_m
        width_ft
        total_sqft
        available_sqft

    Existing inventory tests use master IDs = 1, so Pack 9B
    follows the same established test convention.
    """

    roll = MediaRoll(
        asset_id=f"PACK9B-ASSET-{suffix}",
        roll_number=f"PACK9B-ROLL-{suffix}",
        supplier_id=1,
        manufacturer_id=1,
        product_id=1,
        warehouse_id=1,
        ordered_length_m=30.0,
        actual_length_m=30.0,
        width_ft=4.0,
        total_sqft=total_sqft,
        available_sqft=total_sqft,
        status="AVAILABLE",
        is_active=True,
    )

    db.add(roll)
    db.flush()

    return roll


def _create_allocation(
    db,
    batch,
    item,
    artwork,
    media_roll,
    allocated_sqft=100.0,
):
    """
    Create ProductionAllocation using the current model
    structure directly.
    """

    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        production_batch_id=batch.id,
        media_roll_id=media_roll.id,
        allocated_sqft=allocated_sqft,
        printed_sqft=0,
        wastage_sqft=0,
        balance_sqft=allocated_sqft,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.flush()

    return allocation


def _create_complete_setup(
    db,
    suffix="001",
    batch_number="PACK9B-001",
    artwork_sqft=100.0,
):
    """
    Create a complete Pack 9B production chain:

        Campaign
            ↓
        CampaignVersion
            ↓
        CampaignArtwork
            ↓
        ProductionBatch
            ↓
        ProductionItem
            ↓
        MediaRoll
            ↓
        ProductionAllocation
    """

    printer = _create_printer(db)

    campaign = _create_campaign(
        db,
        suffix=suffix,
    )

    campaign_version = _create_campaign_version(
        db,
        campaign=campaign,
        suffix=suffix,
    )

    artwork = _create_artwork(
        db,
        campaign_version=campaign_version,
        sqft=artwork_sqft,
        suffix=suffix,
    )

    batch = _create_batch(
        db,
        printer=printer,
        batch_number=batch_number,
    )

    item = _create_item(
        db,
        batch=batch,
        artwork=artwork,
        planned_sqft=artwork_sqft,
    )

    media_roll = _create_media_roll(
        db,
        suffix=suffix,
    )

    return {
        "printer": printer,
        "campaign": campaign,
        "campaign_version": campaign_version,
        "artwork": artwork,
        "batch": batch,
        "item": item,
        "media_roll": media_roll,
    }


# ============================================================
# PRODUCTION BATCH TESTS
# ============================================================

def test_production_batch_can_be_created():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    printer = _create_printer(db)

    batch = _create_batch(
        db,
        printer=printer,
    )

    assert batch.id is not None
    assert batch.batch_number == "PACK9B-001"
    assert batch.printer_id == printer.id
    assert batch.status == "PLANNED"

    db.close()


def test_production_item_is_linked_to_batch():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    assert setup["item"].production_batch_id == setup["batch"].id
    assert setup["item"].production_batch.id == setup["batch"].id

    db.close()


def test_production_item_is_linked_to_campaign_artwork():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    assert (
        setup["item"].campaign_artwork_id
        == setup["artwork"].id
    )

    assert (
        setup["item"].campaign_artwork.id
        == setup["artwork"].id
    )

    db.close()


def test_batch_total_planned_sqft_is_calculated():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(
        db,
        artwork_sqft=250.0,
    )

    assert setup["batch"].total_planned_sqft == 250.0

    db.close()


def test_batch_total_printed_sqft_is_calculated():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(
        db,
        artwork_sqft=250.0,
    )

    setup["item"].printed_sqft = 150.0
    db.flush()

    assert setup["batch"].total_printed_sqft == 150.0

    db.close()


def test_batch_total_wastage_sqft_is_calculated():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(
        db,
        artwork_sqft=250.0,
    )

    setup["item"].wastage_sqft = 25.0
    db.flush()

    assert setup["batch"].total_wastage_sqft == 25.0

    db.close()


def test_batch_completion_percentage_is_calculated():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(
        db,
        artwork_sqft=250.0,
    )

    setup["item"].printed_sqft = 125.0
    db.flush()

    assert setup["batch"].completion_percentage == 50.0

    db.close()


# ============================================================
# PRODUCTION ALLOCATION TESTS
# ============================================================

def test_production_allocation_can_be_created():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    allocation = _create_allocation(
        db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=setup["media_roll"],
        allocated_sqft=100.0,
    )

    assert allocation.id is not None
    assert allocation.production_batch_id == setup["batch"].id
    assert allocation.production_item_id == setup["item"].id
    assert allocation.campaign_artwork_id == setup["artwork"].id
    assert allocation.media_roll_id == setup["media_roll"].id
    assert allocation.allocated_sqft == 100.0
    assert allocation.printed_sqft == 0
    assert allocation.wastage_sqft == 0
    assert allocation.balance_sqft == 100.0
    assert allocation.status == "ALLOCATED"

    db.close()


def test_production_allocation_repository_returns_batch_allocations():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    allocation = _create_allocation(
        db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=setup["media_roll"],
        allocated_sqft=100.0,
    )

    allocations = ProductionAllocationRepository.get_by_batch(
        db,
        setup["batch"].id,
    )

    assert len(allocations) == 1
    assert allocations[0].id == allocation.id
    assert allocations[0].production_batch_id == setup["batch"].id

    db.close()


def test_allocation_service_signature_matches_current_contract():
    signature = inspect.signature(
        ProductionAllocationService.allocate
    )

    parameters = list(signature.parameters.keys())

    assert parameters == [
        "db",
        "batch",
        "item",
        "artwork",
        "media_roll",
        "allocated_sqft",
        "status",
    ]


def test_allocation_service_creates_allocation():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=setup["media_roll"],
        allocated_sqft=125.0,
    )

    assert allocation.id is not None
    assert allocation.production_batch_id == setup["batch"].id
    assert allocation.production_item_id == setup["item"].id
    assert allocation.campaign_artwork_id == setup["artwork"].id
    assert allocation.media_roll_id == setup["media_roll"].id
    assert allocation.allocated_sqft == 125.0
    assert allocation.printed_sqft == 0
    assert allocation.wastage_sqft == 0
    assert allocation.balance_sqft == 125.0
    assert allocation.status == "ALLOCATED"

    db.close()


def test_printing_session_is_linked_to_batch():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    session = PrintingSession(
        production_batch_id=setup["batch"].id,
        printer_id=setup["printer"].id,
        planned_sqft=setup["batch"].total_planned_sqft,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    assert session.id is not None
    assert session.production_batch_id == setup["batch"].id
    assert session.printer_id == setup["printer"].id

    db.close()


def test_printing_session_planned_sqft_matches_batch():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(
        db,
        artwork_sqft=300.0,
    )

    session = PrintingSession(
        production_batch_id=setup["batch"].id,
        printer_id=setup["printer"].id,
        planned_sqft=setup["batch"].total_planned_sqft,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    assert session.planned_sqft == 300.0
    assert (
        session.planned_sqft
        == setup["batch"].total_planned_sqft
    )

    db.close()


# ============================================================
# REFRESH / RELATIONSHIP TESTS
# ============================================================

def test_batch_items_and_allocations_survive_refresh():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    allocation = _create_allocation(
        db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=setup["media_roll"],
        allocated_sqft=100.0,
    )

    db.commit()

    batch_id = setup["batch"].id

    db.expire_all()

    batch = db.get(
        ProductionBatch,
        batch_id,
    )

    assert batch is not None
    assert len(batch.production_items) == 1
    assert len(batch.allocations) == 1

    assert (
        batch.production_items[0].id
        == setup["item"].id
    )

    assert (
        batch.allocations[0].id
        == allocation.id
    )

    db.close()


def test_multiple_allocations_are_kept_separately():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    roll_1 = setup["media_roll"]

    roll_2 = _create_media_roll(
        db,
        suffix="002",
    )

    allocation_1 = _create_allocation(
        db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=roll_1,
        allocated_sqft=100.0,
    )

    allocation_2 = _create_allocation(
        db,
        batch=setup["batch"],
        item=setup["item"],
        artwork=setup["artwork"],
        media_roll=roll_2,
        allocated_sqft=150.0,
    )

    allocations = ProductionAllocationRepository.get_by_batch(
        db,
        setup["batch"].id,
    )

    assert len(allocations) == 2

    allocation_ids = {
        allocation.id
        for allocation in allocations
    }

    assert allocation_1.id in allocation_ids
    assert allocation_2.id in allocation_ids

    assert (
        allocations[0].allocated_sqft
        + allocations[1].allocated_sqft
        == 250.0
    )

    db.close()


# ============================================================
# TRANSACTION / ROLLBACK TEST
# ============================================================

def test_allocation_rollback_does_not_persist():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    allocation = ProductionAllocation(
        production_item_id=setup["item"].id,
        campaign_artwork_id=setup["artwork"].id,
        production_batch_id=setup["batch"].id,
        media_roll_id=setup["media_roll"].id,
        allocated_sqft=100.0,
        printed_sqft=0,
        wastage_sqft=0,
        balance_sqft=100.0,
        status="ALLOCATED",
    )

    db.add(allocation)
    db.flush()

    allocation_id = allocation.id

    db.rollback()

    persisted = db.get(
        ProductionAllocation,
        allocation_id,
    )

    assert persisted is None

    db.close()


# ============================================================
# CASCADE DELETE TEST
# ============================================================

def test_deleting_batch_removes_production_items():
    SessionLocal = _get_session_factory()
    db = SessionLocal()

    setup = _create_complete_setup(db)

    item_id = setup["item"].id
    batch_id = setup["batch"].id

    db.delete(setup["batch"])
    db.flush()

    item = db.get(
        ProductionItem,
        item_id,
    )

    batch = db.get(
        ProductionBatch,
        batch_id,
    )

    assert batch is None
    assert item is None

    db.close()
