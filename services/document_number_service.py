from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from models.document_sequence import DocumentSequence


class DocumentNumberService:
    """
    Central Document Number Engine

    Examples

    PB-2026-000001

    MR-2026-000001

    DS-2026-000001
    """

    @staticmethod
    def generate(
        db: Session,
        document_type: str,
    ) -> str:

        sequence = (
            db.query(DocumentSequence)
            .filter(
                DocumentSequence.document_type == document_type
            )
            .first()
        )

        if sequence is None:

            raise Exception(
                f"Document Sequence not found : {document_type}"
            )

        year = datetime.now().year

        sequence.last_number += 1

        number = sequence.last_number

        db.flush()

        db.commit()

        db.refresh(sequence)

        return (
            f"{sequence.prefix}-"
            f"{year}-"
            f"{number:06d}"
        )
