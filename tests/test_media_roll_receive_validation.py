from datetime import date

from models.media_roll import MediaRoll
from services.media_roll_service import MediaRollService


def build_roll(
    manufacturer_id,
    product_id,
    supplier_id=1,
    warehouse_id=1,
    manufacturer_roll_no="TEST-VALIDATION-001",
):

    return MediaRoll(
        supplier_id=supplier_id,
        manufacturer_id=manufacturer_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        manufacturer_roll_no=manufacturer_roll_no,
        purchase_order="TEST-PO",
        invoice_number="TEST-INV",
        invoice_date=date.today(),
        ordered_length_m=50.0,
        actual_length_m=50.0,
        width_ft=4.0,
        total_sqft=656.168,
        available_sqft=656.168,
        remarks="Validation test",
    )


def test_missing_manufacturer_roll_number(db_session):

    roll = build_roll(
        manufacturer_id=1,
        product_id=1,
        manufacturer_roll_no="",
    )

    result = MediaRollService.receive(
        db=db_session,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is False

    assert any(
        "Manufacturer Roll Number is required"
        in error
        for error in result.errors
    )


def test_duplicate_manufacturer_roll_number(
    db_session,
):

    first_roll = build_roll(
        manufacturer_id=1,
        product_id=1,
        manufacturer_roll_no=(
            "DUPLICATE-ROLL-001"
        ),
    )

    first_result = MediaRollService.receive(
        db=db_session,
        media_roll=first_roll,
        user="TEST",
    )

    assert first_result.success is True


    second_roll = build_roll(
        manufacturer_id=1,
        product_id=1,
        manufacturer_roll_no=(
            "DUPLICATE-ROLL-001"
        ),
    )

    second_result = MediaRollService.receive(
        db=db_session,
        media_roll=second_roll,
        user="TEST",
    )

    assert second_result.success is False

    assert any(
        "has already been received"
        in error
        for error in second_result.errors
    )


def test_invalid_dimensions_are_rejected(
    db_session,
):

    roll = build_roll(
        manufacturer_id=1,
        product_id=1,
        manufacturer_roll_no=(
            "INVALID-DIMENSION-001"
        ),
    )

    roll.actual_length_m = 0

    result = MediaRollService.receive(
        db=db_session,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is False

    assert any(
        "Actual length must be greater than zero"
        in error
        for error in result.errors
    )
