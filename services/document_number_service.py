from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from models.document_sequence import DocumentSequence


class DocumentNumberService:
    """
    Central document numbering engine.

    Examples:

        PB-2026-000001
        MR-2026-000154
        DS-2026-000010

    IMPORTANT:
    This service NEVER commits.

    The caller owns the transaction.
    """

    @staticmethod
    def generate(
        db: Session,
        document_type: str,
    ) -> str:

        sequence = (
            db.query(DocumentSequence)
            .filter(
                DocumentSequence.document_type
                == document_type
            )
            .first()
        )

        if sequence is None:
            raise ValueError(
                f"No document sequence found for {document_type}"
            )

        year = datetime.now().year

        sequence.last_number += 1

        # Make the new sequence value visible
        # to the current transaction without committing.
        db.flush()

        return (
            f"{sequence.prefix}-"
            f"{year}-"
            f"{sequence.last_number:06d}"
        )
