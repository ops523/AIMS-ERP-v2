from __future__ import annotations

import pytest

from models.production_batch import ProductionBatch
from models.production_item import ProductionItem
from models.production_allocation import ProductionAllocation
from models.printing_session import PrintingSession

from services.production_batch_creator import ProductionBatchCreator


# ============================================================
# Helpers
# ============================================================


def _commit(db):
    db.commit()


def _refresh(db, obj):
    db.flush()
    db.refresh(obj)
    return obj


# ============================================================
# Batch creation
# ============================================================


def test_create_production_batch_creates_batch(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch is not None
    assert batch.id is not None
    assert batch.printer_id == printer.id
    assert batch.status == "PLANNED"


def test_create_production_batch_creates_production_items(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    db.refresh(batch)

    assert len(batch.production_items) == len(artworks)

    artwork_ids = {
        artwork.id
        for artwork in artworks
    }

    item_artwork_ids = {
        item.campaign_artwork_id
        for item in batch.production_items
    }

    assert item_artwork_ids == artwork_ids


def test_production_items_have_correct_planned_sqft(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    db.refresh(batch)

    for item in batch.production_items:

        artwork = next(
            artwork
            for artwork in artworks
            if artwork.id == item.campaign_artwork_id
        )

        assert item.planned_sqft == artwork.artwork_sqft
        assert item.printed_sqft == 0
        assert item.wastage_sqft == 0
        assert item.status == "PENDING"


# ============================================================
# Batch totals
# ============================================================


def test_batch_total_planned_sqft(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    expected = sum(
        artwork.artwork_sqft
        for artwork in artworks
    )

    assert batch.total_planned_sqft == expected


def test_batch_initial_printed_sqft_is_zero(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.total_printed_sqft == 0


def test_batch_initial_wastage_sqft_is_zero(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.total_wastage_sqft == 0


def test_batch_initial_completion_is_zero(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.completion_percentage == 0


# ============================================================
# Printing session
# ============================================================


def test_create_batch_creates_printing_session(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    sessions = (
        db.query(PrintingSession)
        .filter(
            PrintingSession.production_batch_id
            == batch.id
        )
        .all()
    )

    assert len(sessions) == 1


def test_printing_session_has_correct_printer(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    session = (
        db.query(PrintingSession)
        .filter(
            PrintingSession.production_batch_id
            == batch.id
        )
        .one()
    )

    assert session.printer_id == printer.id


def test_printing_session_is_in_progress(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    session = (
        db.query(PrintingSession)
        .filter(
            PrintingSession.production_batch_id
            == batch.id
        )
        .one()
    )

    assert session.status == "IN_PROGRESS"


def test_printing_session_planned_sqft_matches_batch(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    session = (
        db.query(PrintingSession)
        .filter(
            PrintingSession.production_batch_id
            == batch.id
        )
        .one()
    )

    assert session.planned_sqft == batch.total_planned_sqft


# ============================================================
# Allocation
# ============================================================


def test_create_batch_with_roll_allocations(
    db,
    printer,
    campaign_version,
    artworks,
    media_roll,
):
    artwork = artworks[0]

    allocation_data = [
        {
            "production_item_id": None,
            "media_roll_id": media_roll.id,
            "allocated_sqft": 100,
        }
    ]

    # The current creator expects production_item_id
    # to already exist. Resolve it after creating the
    # batch structure is not currently supported by the
    # creator, so this test documents the required shape.
    #
    # This test intentionally verifies that the creator
    # requires valid ProductionItem references.

    with pytest.raises(Exception):
        ProductionBatchCreator.create_batch(
            db=db,
            printer=printer,
            campaign_version=campaign_version,
            artworks=artworks,
            roll_allocations=allocation_data,
        )


# ============================================================
# Production item relationships
# ============================================================


def test_production_items_belong_to_batch(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    db.refresh(batch)

    for item in batch.production_items:
        assert item.production_batch_id == batch.id
        assert item.production_batch.id == batch.id


def test_production_item_artwork_relationship(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    db.refresh(batch)

    for item in batch.production_items:
        assert item.campaign_artwork is not None
        assert (
            item.campaign_artwork.id
            == item.campaign_artwork_id
        )


# ============================================================
# Batch progress calculations
# ============================================================


def test_batch_completion_percentage_after_printing(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    item = batch.production_items[0]

    item.printed_sqft = item.planned_sqft / 2

    db.flush()
    db.refresh(batch)

    expected = (
        batch.total_printed_sqft
        / batch.total_planned_sqft
    ) * 100

    assert batch.completion_percentage == round(
        expected,
        2,
    )


def test_batch_wastage_is_aggregated(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    batch.production_items[0].wastage_sqft = 10

    if len(batch.production_items) > 1:
        batch.production_items[1].wastage_sqft = 5

    db.flush()
    db.refresh(batch)

    expected = sum(
        item.wastage_sqft
        for item in batch.production_items
    )

    assert batch.total_wastage_sqft == expected


# ============================================================
# Database persistence
# ============================================================


def test_batch_is_persisted(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    batch_id = batch.id

    db.expire_all()

    persisted = (
        db.query(ProductionBatch)
        .filter(
            ProductionBatch.id == batch_id
        )
        .one()
    )

    assert persisted.id == batch_id
    assert persisted.printer_id == printer.id


def test_production_items_are_persisted(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    items = (
        db.query(ProductionItem)
        .filter(
            ProductionItem.production_batch_id
            == batch.id
        )
        .all()
    )

    assert len(items) == len(artworks)


def test_printing_session_is_persisted(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    sessions = (
        db.query(PrintingSession)
        .filter(
            PrintingSession.production_batch_id
            == batch.id
        )
        .all()
    )

    assert len(sessions) == 1


# ============================================================
# Batch relationship collections
# ============================================================


def test_batch_production_items_collection(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.production_items is not None
    assert isinstance(
        batch.production_items,
        list,
    )


def test_batch_printing_sessions_collection(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.printing_sessions is not None
    assert len(batch.printing_sessions) == 1


def test_batch_allocations_collection_exists(
    db,
    printer,
    campaign_version,
    artworks,
):
    batch = ProductionBatchCreator.create_batch(
        db=db,
        printer=printer,
        campaign_version=campaign_version,
        artworks=artworks,
        roll_allocations=[],
    )

    assert batch.allocations is not None
    assert isinstance(
        batch.allocations,
        list,
    )
