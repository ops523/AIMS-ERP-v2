from __future__ import annotations

import inspect
from datetime import date

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
# Test database
# ============================================================

@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=True,
        autocommit=False,
    )

    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


# ============================================================
# Fixtures / helpers
# ============================================================

def _create_printer(db):
    """
    Create the minimum Printer record required by ProductionBatch.
    """

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
    Create a valid Campaign using the mandatory fields
    currently required by the Campaign model.
    """

    campaign = Campaign(
        campaign_code="PACK9B-TEST-CAMPAIGN",
        client_name="PACK9B TEST CLIENT",
        brand_name="PACK9B TEST BRAND",
        campaign_name="PACK9B TEST CAMPAIGN",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )

    db.add(campaign)
    db.flush()

    return campaign


def _create_campaign_version(db, campaign):
    """
    CampaignArtwork belongs to CampaignVersion, not directly
    to Campaign.
    """

    version = CampaignVersion(
        campaign_id=campaign.id,
        version_no=1,
        version_name="V1",
        import_batch="PACK9B-TEST-IMPORT",
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
    sqft=250.0,
    artwork_code="PACK9B-ART-001",
):
    """
    Create a valid CampaignArtwork.
    """

    artwork = CampaignArtwork(
        campaign_version_id=campaign_version.id,
        artwork_code=artwork_code,
        artwork_name="PACK9B TEST ARTWORK",
        file_name="pack9b_test.jpg",
        width_ft=10.0,
        height_ft=25.0,
        artwork_sqft=sqft,
        assigned_walls=1,
    )

    db.add(artwork)
    db.flush()

    return artwork


def _create_printer_and_batch(
    db,
    batch_number="PACK9B-001",
    status="PLANNED",
):
    printer = _create_printer(db)

    batch = ProductionBatch(
        batch_number=batch_number,
        printer_id=printer.id,
        status=status,
    )

    db.add(batch)
    db.flush()

    return printer, batch


def _create_item(
    db,
    batch,
    artwork,
    planned_sqft=None,
    printed_sqft=0,
    wastage_sqft=0,
    status="PENDING",
):
    if planned_sqft is None:
        planned_sqft = artwork.artwork_sqft

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


def _create_media_roll(db):
    """
    Create a MediaRoll using the fields currently supported by
    the model.

    The helper intentionally discovers the model's supported
    fields instead of passing obsolete manufacturer_roll_number
    arguments.
    """

    mapper = MediaRoll.__mapper__

    values = {}

    if "roll_number" in mapper.columns:
        values["roll_number"] = "PACK9B-ROLL-001"

    if "roll_code" in mapper.columns:
        values["roll_code"] = "PACK9B-ROLL-001"

    if "width_ft" in mapper.columns:
        values["width_ft"] = 4.0

    if "ordered_length_ft" in mapper.columns:
        values["ordered_length_ft"] = 100.0

    if "actual_length_ft" in mapper.columns:
        values["actual_length_ft"] = 100.0

    if "total_sqft" in mapper.columns:
        values["total_sqft"] = 400.0

    if "ordered_sqft" in mapper.columns:
        values["ordered_sqft"] = 400.0

    if "actual_sqft" in mapper.columns:
        values["actual_sqft"] = 400.0

    if "status" in mapper.columns:
        values["status"] = "AVAILABLE"

    roll = MediaRoll(**values)

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
    status="ALLOCATED",
):
    """
    Create a ProductionAllocation using every mandatory
    foreign-key relationship in the current model.
    """

    allocation = ProductionAllocation(
        production_batch_id=batch.id,
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        media_roll_id=media_roll.id,
        allocated_sqft=allocated_sqft,
        printed_sqft=0,
        wastage_sqft=0,
        balance_sqft=allocated_sqft,
        status=status,
    )

    db.add(allocation)
    db.flush()

    return allocation


def _create_complete_context(
    db,
    sqft=250.0,
    batch_number="PACK9B-001",
    artwork_code="PACK9B-ART-001",
):
    printer, batch = _create_printer_and_batch(
        db,
        batch_number=batch_number,
    )

    campaign = _create_campaign(db)

    version = _create_campaign_version(
        db,
        campaign,
    )

    artwork = _create_artwork(
        db,
        version,
        sqft=sqft,
        artwork_code=artwork_code,
    )

    item = _create_item(
        db,
        batch,
        artwork,
        planned_sqft=sqft,
    )

    media_roll = _create_media_roll(db)

    return {
        "printer": printer,
        "batch": batch,
        "campaign": campaign,
        "version": version,
        "artwork": artwork,
        "item": item,
        "media_roll": media_roll,
    }


# ============================================================
# Production Batch
# ============================================================

def test_production_batch_can_be_created(db):

    printer, batch = _create_printer_and_batch(db)

    assert batch.id is not None
    assert batch.batch_number == "PACK9B-001"
    assert batch.printer_id == printer.id
    assert batch.status == "PLANNED"


def test_production_item_is_linked_to_batch(db):

    ctx = _create_complete_context(db)

    item = ctx["item"]
    batch = ctx["batch"]

    assert item.production_batch_id == batch.id
    assert item.production_batch.id == batch.id


def test_production_item_is_linked_to_campaign_artwork(db):

    ctx = _create_complete_context(db)

    item = ctx["item"]
    artwork = ctx["artwork"]

    assert item.campaign_artwork_id == artwork.id
    assert item.campaign_artwork.id == artwork.id


def test_batch_total_planned_sqft_is_calculated(db):

    ctx = _create_complete_context(
        db,
        sqft=250.0,
    )

    batch = ctx["batch"]
    artwork = ctx["artwork"]

    item2 = _create_item(
        db,
        batch,
        artwork,
        planned_sqft=150.0,
    )

    assert item2.id is not None
    assert batch.total_planned_sqft == 400.0


def test_batch_total_printed_sqft_is_calculated(db):

    ctx = _create_complete_context(
        db,
        sqft=250.0,
    )

    batch = ctx["batch"]
    item = ctx["item"]

    item.printed_sqft = 175.0
    db.flush()

    assert batch.total_printed_sqft == 175.0


def test_batch_total_wastage_sqft_is_calculated(db):

    ctx = _create_complete_context(
        db,
        sqft=250.0,
    )

    batch = ctx["batch"]
    item = ctx["item"]

    item.wastage_sqft = 25.0
    db.flush()

    assert batch.total_wastage_sqft == 25.0


def test_batch_completion_percentage_is_calculated(db):

    ctx = _create_complete_context(
        db,
        sqft=250.0,
    )

    batch = ctx["batch"]
    item = ctx["item"]

    item.printed_sqft = 125.0
    db.flush()

    assert batch.completion_percentage == 50.0


# ============================================================
# Production Allocation
# ============================================================

def test_production_allocation_can_be_created(db):

    ctx = _create_complete_context(db)

    allocation = _create_allocation(
        db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    assert allocation.id is not None
    assert allocation.production_batch_id == ctx["batch"].id
    assert allocation.production_item_id == ctx["item"].id
    assert allocation.campaign_artwork_id == ctx["artwork"].id
    assert allocation.media_roll_id == ctx["media_roll"].id
    assert allocation.allocated_sqft == 100.0
    assert allocation.printed_sqft == 0
    assert allocation.wastage_sqft == 0
    assert allocation.balance_sqft == 100.0
    assert allocation.status == "ALLOCATED"


def test_production_allocation_repository_returns_batch_allocations(db):

    ctx = _create_complete_context(db)

    allocation = _create_allocation(
        db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    results = ProductionAllocationRepository.get_by_batch(
        db,
        ctx["batch"].id,
    )

    assert len(results) == 1
    assert results[0].id == allocation.id
    assert results[0].production_batch_id == ctx["batch"].id


def test_allocation_service_signature_matches_current_contract():

    signature = inspect.signature(
        ProductionAllocationService.allocate,
    )

    parameters = list(signature.parameters.values())

    names = [
        parameter.name
        for parameter in parameters
    ]

    assert names == [
        "db",
        "batch",
        "item",
        "artwork",
        "media_roll",
        "allocated_sqft",
        "status",
    ]


def test_allocation_service_creates_allocation(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=120.0,
    )

    assert allocation.id is not None
    assert allocation.production_batch_id == ctx["batch"].id
    assert allocation.production_item_id == ctx["item"].id
    assert allocation.campaign_artwork_id == ctx["artwork"].id
    assert allocation.media_roll_id == ctx["media_roll"].id
    assert allocation.allocated_sqft == 120.0
    assert allocation.printed_sqft == 0
    assert allocation.wastage_sqft == 0
    assert allocation.balance_sqft == 120.0
    assert allocation.status == "ALLOCATED"


def test_allocation_service_rejects_zero_quantity(db):

    ctx = _create_complete_context(db)

    with pytest.raises(
        ValueError,
        match="Allocated quantity must be greater than zero",
    ):
        ProductionAllocationService.allocate(
            db=db,
            batch=ctx["batch"],
            item=ctx["item"],
            artwork=ctx["artwork"],
            media_roll=ctx["media_roll"],
            allocated_sqft=0,
        )


def test_allocation_service_rejects_negative_quantity(db):

    ctx = _create_complete_context(db)

    with pytest.raises(
        ValueError,
        match="Allocated quantity must be greater than zero",
    ):
        ProductionAllocationService.allocate(
            db=db,
            batch=ctx["batch"],
            item=ctx["item"],
            artwork=ctx["artwork"],
            media_roll=ctx["media_roll"],
            allocated_sqft=-10,
        )


# ============================================================
# Allocation calculations
# ============================================================

def test_allocation_completion_percentage_starts_at_zero(db):

    ctx = _create_complete_context(db)

    allocation = _create_allocation(
        db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    assert allocation.completion_percentage == 0.0


def test_allocation_can_be_partially_printed(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    ProductionAllocationService.update_printed_quantity(
        db=db,
        allocation=allocation,
        printed_sqft=60.0,
        wastage_sqft=0,
    )

    assert allocation.printed_sqft == 60.0
    assert allocation.wastage_sqft == 0
    assert allocation.balance_sqft == 40.0
    assert allocation.status == "PARTIALLY_PRINTED"
    assert allocation.completion_percentage == 60.0


def test_allocation_can_be_completed(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    ProductionAllocationService.update_printed_quantity(
        db=db,
        allocation=allocation,
        printed_sqft=100.0,
        wastage_sqft=0,
    )

    assert allocation.printed_sqft == 100.0
    assert allocation.balance_sqft == 0.0
    assert allocation.status == "COMPLETED"
    assert allocation.completion_percentage == 100.0


def test_allocation_wastage_reduces_balance(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    ProductionAllocationService.update_printed_quantity(
        db=db,
        allocation=allocation,
        printed_sqft=70.0,
        wastage_sqft=10.0,
    )

    assert allocation.printed_sqft == 70.0
    assert allocation.wastage_sqft == 10.0
    assert allocation.balance_sqft == 20.0
    assert allocation.status == "PARTIALLY_PRINTED"


def test_allocation_cannot_process_more_than_allocated(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    with pytest.raises(
        ValueError,
        match="cannot exceed allocated quantity",
    ):
        ProductionAllocationService.update_printed_quantity(
            db=db,
            allocation=allocation,
            printed_sqft=80.0,
            wastage_sqft=30.0,
        )


# ============================================================
# Batch relationships
# ============================================================

def test_batch_items_and_allocations_survive_refresh(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    db.commit()

    db.expire_all()

    batch = db.get(
        ProductionBatch,
        ctx["batch"].id,
    )

    assert batch is not None
    assert len(batch.production_items) == 1
    assert len(batch.allocations) == 1

    refreshed_allocation = batch.allocations[0]

    assert refreshed_allocation.id == allocation.id
    assert refreshed_allocation.production_batch_id == batch.id
    assert refreshed_allocation.production_item_id == ctx["item"].id
    assert refreshed_allocation.campaign_artwork_id == ctx["artwork"].id
    assert refreshed_allocation.media_roll_id == ctx["media_roll"].id


def test_multiple_allocations_are_kept_separately(db):

    ctx = _create_complete_context(db)

    roll2 = _create_media_roll(db)

    allocation1 = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    allocation2 = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=roll2,
        allocated_sqft=150.0,
    )

    results = ProductionAllocationRepository.get_by_batch(
        db,
        ctx["batch"].id,
    )

    assert len(results) == 2

    ids = {
        allocation.id
        for allocation in results
    }

    assert allocation1.id in ids
    assert allocation2.id in ids

    quantities = sorted(
        allocation.allocated_sqft
        for allocation in results
    )

    assert quantities == [100.0, 150.0]


def test_allocation_rollback_does_not_persist(db):

    ctx = _create_complete_context(db)

    allocation = ProductionAllocationService.allocate(
        db=db,
        batch=ctx["batch"],
        item=ctx["item"],
        artwork=ctx["artwork"],
        media_roll=ctx["media_roll"],
        allocated_sqft=100.0,
    )

    allocation_id = allocation.id

    db.rollback()

    result = db.get(
        ProductionAllocation,
        allocation_id,
    )

    assert result is None


# ============================================================
# Cascade behaviour
# ============================================================

def test_deleting_batch_removes_production_items(db):

    ctx = _create_complete_context(db)

    batch_id = ctx["batch"].id
    item_id = ctx["item"].id

    db.delete(ctx["batch"])
    db.commit()

    assert db.get(
        ProductionBatch,
        batch_id,
    ) is None

    assert db.get(
        ProductionItem,
        item_id,
    ) is None


# ============================================================
# Printing Session
# ============================================================

def test_printing_session_is_linked_to_batch(db):

    ctx = _create_complete_context(db)

    session = PrintingSession(
        production_batch_id=ctx["batch"].id,
        printer_id=ctx["printer"].id,
        planned_sqft=ctx["batch"].total_planned_sqft,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    assert session.id is not None
    assert session.production_batch_id == ctx["batch"].id
    assert session.printer_id == ctx["printer"].id


def test_printing_session_planned_sqft_matches_batch(db):

    ctx = _create_complete_context(
        db,
        sqft=250.0,
    )

    session = PrintingSession(
        production_batch_id=ctx["batch"].id,
        printer_id=ctx["printer"].id,
        planned_sqft=ctx["batch"].total_planned_sqft,
        status="IN_PROGRESS",
    )

    db.add(session)
    db.flush()

    assert session.planned_sqft == ctx["batch"].total_planned_sqft
