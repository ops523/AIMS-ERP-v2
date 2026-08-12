from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base

import models

from models.document_sequence import (
    DocumentSequence,
)

from services.document_number_service import (
    DocumentNumberService,
)


def create_test_db():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(
        bind=engine
    )

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return Session()


def test_document_number_rolls_back():

    db = create_test_db()

    sequence = DocumentSequence(
        document_type="MEDIA_ROLL",
        prefix="MR",
        last_number=10,
    )

    db.add(sequence)

    db.commit()

    number = DocumentNumberService.generate(
        db=db,
        document_type="MEDIA_ROLL",
    )

    assert number.endswith(
        "-000011"
    )

    # Simulate failed business transaction.
    db.rollback()

    refreshed = (
        db.query(DocumentSequence)
        .filter(
            DocumentSequence.document_type
            == "MEDIA_ROLL"
        )
        .first()
    )

    assert refreshed.last_number == 10

    db.close()


def test_document_number_commits_when_outer_transaction_commits():

    db = create_test_db()

    sequence = DocumentSequence(
        document_type="MEDIA_ROLL",
        prefix="MR",
        last_number=10,
    )

    db.add(sequence)

    db.commit()

    number = DocumentNumberService.generate(
        db=db,
        document_type="MEDIA_ROLL",
    )

    assert number.endswith(
        "-000011"
    )

    # The OUTER business transaction commits.
    db.commit()

    refreshed = (
        db.query(DocumentSequence)
        .filter(
            DocumentSequence.document_type
            == "MEDIA_ROLL"
        )
        .first()
    )

    assert refreshed.last_number == 11

    db.close()
