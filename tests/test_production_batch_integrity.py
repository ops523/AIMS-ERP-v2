from __future__ import annotations

from datetime import date

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.production_batch import ProductionBatch
from models.production_item import ProductionItem
from models.production_allocation import ProductionAllocation
from models.printing_session import PrintingSession


# ============================================================
# TEST DB
# ============================================================

def _get_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )


# ============================================================
# FIXTURES
# ============================================================

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
    Create a valid Campaign fixture according to the current
    Campaign model requirements.
    """

    from models.campaign import Campaign

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
    Create the CampaignVersion required by CampaignArtwork.
    """

    from models.campaign_version import CampaignVersion

    version = CampaignVersion(
        campaign_id=campaign.id,
        version_no=1,
        version_name="V1",
        import_batch="PACK9B-TEST-IMPORT",
        total_locations=1,
        total_walls=1,
        total_sqft=100,
    )

    db.add(version)
    db.flush()

    return version


def _create_artwork(
    db,
    campaign_version,
    sqft=100.0,
):
    from models.campaign_artwork import CampaignArtwork

    count = (
        db.query(CampaignArtwork)
        .count()
    )

    artwork = CampaignArtwork(
        campaign_version_id=campaign_version.id,
        artwork_code=f"PACK9B-ART-{count + 1:03d}",
        artwork_name=f"PACK9B TEST ARTWORK {count + 1}",
        file_name=f"pack9b-test-{count + 1}.jpg",
        width_ft=10,
        height_ft=10,
        artwork_sqft=sqft,
        assigned_walls=1,
    )

    db.add(artwork)
    db.flush()

    return artwork


def _create_media_roll(db, roll_number="PACK9B-ROLL-001"):
    """
    Create a minimal MediaRoll required by ProductionAllocation.
    """

    from models.media_roll import MediaRoll

    roll = MediaRoll(
        manufacturer_roll_number=roll_number,
    )

    db.add(roll)
    db.flush()

    return roll


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
):
    item = ProductionItem(
        production_batch_id=batch.id,
        campaign_artwork_id=artwork.id,
        planned_sqft=planned_sqft,
        printed_sqft=printed_sqft,
        wastage_sqft=wastage_sqft,
        status="PENDING",
    )

    db.add(item)
    db.flush()

    return item


def _create_allocation(
    db,
    item,
    artwork,
    media_roll,
    allocated_sqft=100.0,
    consumed_sqft=0.0,
    wastage_sqft=0.0,
):
    allocation = ProductionAllocation(
        production_item_id=item.id,
        campaign_artwork_id=artwork.id,
        media_roll_id=media_roll.id,
        allocated_sqft=allocated_sqft,
        consumed_sqft=consumed_sqft,
        wastage_sqft=wastage_sqft,
        status="RESERVED",
    )

    db.add(allocation)
    db.flush()

    return allocation


# ============================================================
# BASIC BATCH TESTS
# ============================================================

def test_production_batch_can_be_created():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)

        batch = _create_batch(
            db,
            printer,
        )

        assert batch.id is not None
        assert batch.batch_number == "PACK9B-001"
        assert batch.printer_id == printer.id
        assert batch.status == "PLANNED"

    finally:
        db.rollback()
        db.close()


def test_production_item_is_linked_to_batch():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)

        item = _create_item(
            db,
            batch,
            artwork,
            planned_sqft=250,
        )

        assert item.production_batch_id == batch.id
        assert item.production_batch.id == batch.id

    finally:
        db.rollback()
        db.close()


def test_production_item_is_linked_to_campaign_artwork():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(
            db,
            version,
            sqft=250,
        )

        batch = _create_batch(db, printer)

        item = _create_item(
            db,
            batch,
            artwork,
            planned_sqft=250,
        )

        assert item.campaign_artwork_id == artwork.id
        assert item.campaign_artwork.id == artwork.id

    finally:
        db.rollback()
        db.close()


# ============================================================
# BATCH CALCULATIONS
# ============================================================

def test_batch_total_planned_sqft_is_calculated():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)

        artwork_1 = _create_artwork(
            db,
            version,
            sqft=100,
        )

        artwork_2 = _create_artwork(
            db,
            version,
            sqft=200,
        )

        batch = _create_batch(db, printer)

        _create_item(
            db,
            batch,
            artwork_1,
            planned_sqft=100,
        )

        _create_item(
            db,
            batch,
            artwork_2,
            planned_sqft=200,
        )

        assert batch.total_planned_sqft == 300

    finally:
        db.rollback()
        db.close()


def test_batch_total_printed_sqft_is_calculated():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version, sqft=250)

        batch = _create_batch(db, printer)

        _create_item(
            db,
            batch,
            artwork,
            planned_sqft=250,
            printed_sqft=175,
        )

        assert batch.total_printed_sqft == 175

    finally:
        db.rollback()
        db.close()


def test_batch_total_wastage_sqft_is_calculated():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version, sqft=250)

        batch = _create_batch(db, printer)

        _create_item(
            db,
            batch,
            artwork,
            planned_sqft=250,
            printed_sqft=200,
            wastage_sqft=50,
        )

        assert batch.total_wastage_sqft == 50

    finally:
        db.rollback()
        db.close()


def test_batch_completion_percentage_is_calculated():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version, sqft=250)

        batch = _create_batch(db, printer)

        _create_item(
            db,
            batch,
            artwork,
            planned_sqft=250,
            printed_sqft=125,
        )

        assert batch.completion_percentage == 50

    finally:
        db.rollback()
        db.close()


# ============================================================
# ALLOCATION TESTS
# ============================================================

def test_production_allocation_can_be_created():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)

        item = _create_item(
            db,
            batch,
            artwork,
        )

        roll = _create_media_roll(db)

        allocation = _create_allocation(
            db,
            item,
            artwork,
            roll,
            allocated_sqft=100,
        )

        assert allocation.id is not None
        assert allocation.production_item_id == item.id
        assert allocation.media_roll_id == roll.id
        assert allocation.allocated_sqft == 100

    finally:
        db.rollback()
        db.close()


def test_production_allocation_repository_returns_batch_allocations():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        from repositories.production_allocation_repository import (
            ProductionAllocationRepository,
        )

        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)
        item = _create_item(db, batch, artwork)
        roll = _create_media_roll(db)

        allocation = _create_allocation(
            db,
            item,
            artwork,
            roll,
            allocated_sqft=100,
        )

        result = ProductionAllocationRepository.get_by_batch(
            db,
            batch.id,
        )

        assert len(result) == 1
        assert result[0].id == allocation.id

    finally:
        db.rollback()
        db.close()


def test_allocation_service_creates_allocation():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        from services.production_allocation_service import (
            ProductionAllocationService,
        )

        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)
        item = _create_item(db, batch, artwork)
        roll = _create_media_roll(db)

        allocation = ProductionAllocationService.allocate(
            db=db,
            item=item,
            artwork=artwork,
            media_roll=roll,
            allocated_sqft=100,
        )

        assert allocation.id is not None
        assert allocation.production_item_id == item.id
        assert allocation.media_roll_id == roll.id
        assert allocation.allocated_sqft == 100

    finally:
        db.rollback()
        db.close()


# ============================================================
# PRINTING SESSION
# ============================================================

def test_printing_session_is_linked_to_batch():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        batch = _create_batch(db, printer)

        session = PrintingSession(
            production_batch_id=batch.id,
            printer_id=printer.id,
            planned_sqft=100,
            status="IN_PROGRESS",
        )

        db.add(session)
        db.flush()

        assert session.id is not None
        assert session.production_batch_id == batch.id
        assert session.production_batch.id == batch.id

    finally:
        db.rollback()
        db.close()


def test_printing_session_planned_sqft_matches_batch():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version, sqft=300)

        batch = _create_batch(db, printer)

        _create_item(
            db,
            batch,
            artwork,
            planned_sqft=300,
        )

        session = PrintingSession(
            production_batch_id=batch.id,
            printer_id=printer.id,
            planned_sqft=batch.total_planned_sqft,
            status="IN_PROGRESS",
        )

        db.add(session)
        db.flush()

        assert session.planned_sqft == batch.total_planned_sqft
        assert session.planned_sqft == 300

    finally:
        db.rollback()
        db.close()


# ============================================================
# REFRESH / RELATIONSHIP INTEGRITY
# ============================================================

def test_batch_items_and_allocations_survive_refresh():
    create_test_db = _get_session_factory()
    db = create_test_db

    try:
        session = db()

        printer = _create_printer(session)
        campaign = _create_campaign(session)
        version = _create_campaign_version(session, campaign)
        artwork = _create_artwork(session, version)

        batch = _create_batch(session, printer)
        item = _create_item(session, batch, artwork)

        roll = _create_media_roll(session)

        allocation = _create_allocation(
            session,
            item,
            artwork,
            roll,
        )

        session.commit()

        batch_id = batch.id

        session.expire_all()

        refreshed = session.get(
            ProductionBatch,
            batch_id,
        )

        assert refreshed is not None
        assert len(refreshed.production_items) == 1
        assert len(refreshed.allocations) == 1
        assert refreshed.production_items[0].id == item.id
        assert refreshed.allocations[0].id == allocation.id

    finally:
        try:
            session.rollback()
            session.close()
        except Exception:
            pass


def test_multiple_allocations_are_kept_separately():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        from repositories.production_allocation_repository import (
            ProductionAllocationRepository,
        )

        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version, sqft=200)

        batch = _create_batch(db, printer)
        item = _create_item(
            db,
            batch,
            artwork,
            planned_sqft=200,
        )

        roll_1 = _create_media_roll(
            db,
            "PACK9B-ROLL-001",
        )

        roll_2 = _create_media_roll(
            db,
            "PACK9B-ROLL-002",
        )

        allocation_1 = _create_allocation(
            db,
            item,
            artwork,
            roll_1,
            allocated_sqft=100,
        )

        allocation_2 = _create_allocation(
            db,
            item,
            artwork,
            roll_2,
            allocated_sqft=100,
        )

        result = ProductionAllocationRepository.get_by_batch(
            db,
            batch.id,
        )

        assert len(result) == 2

        ids = {
            allocation.id
            for allocation in result
        }

        assert allocation_1.id in ids
        assert allocation_2.id in ids

        roll_ids = {
            allocation.media_roll_id
            for allocation in result
        }

        assert roll_1.id in roll_ids
        assert roll_2.id in roll_ids

    finally:
        db.rollback()
        db.close()


def test_allocation_rollback_does_not_persist():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        from repositories.production_allocation_repository import (
            ProductionAllocationRepository,
        )

        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)
        item = _create_item(db, batch, artwork)

        roll = _create_media_roll(db)

        allocation = _create_allocation(
            db,
            item,
            artwork,
            roll,
        )

        allocation_id = allocation.id

        db.rollback()

        result = ProductionAllocationRepository.get_by_batch(
            db,
            batch.id,
        )

        assert all(
            existing.id != allocation_id
            for existing in result
        )

    finally:
        db.rollback()
        db.close()


# ============================================================
# CASCADE DELETE
# ============================================================

def test_deleting_batch_removes_production_items():
    create_test_db = _get_session_factory()
    db = create_test_db()

    try:
        printer = _create_printer(db)
        campaign = _create_campaign(db)
        version = _create_campaign_version(db, campaign)
        artwork = _create_artwork(db, version)

        batch = _create_batch(db, printer)

        item = _create_item(
            db,
            batch,
            artwork,
        )

        item_id = item.id
        batch_id = batch.id

        db.delete(batch)
        db.flush()

        assert db.get(
            ProductionBatch,
            batch_id,
        ) is None

        assert db.get(
            ProductionItem,
            item_id,
        ) is None

    finally:
        db.rollback()
        db.close()
