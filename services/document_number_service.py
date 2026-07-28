from sqlalchemy.orm import Session

from models.document_sequence import DocumentSequence


class DocumentNumberService:

    @staticmethod
    def next(
        db: Session,
        document_type: str,
        prefix: str,
    ) -> str:

        sequence = (
            db.query(DocumentSequence)
            .filter(
                DocumentSequence.document_type == document_type
            )
            .first()
        )

        if sequence is None:

            sequence = DocumentSequence(
                document_type=document_type,
                prefix=prefix,
                last_number=0,
            )

            db.add(sequence)
            db.flush()

        sequence.last_number += 1

        db.commit()

        db.refresh(sequence)

        return (
            f"{sequence.prefix}"
            f"{sequence.last_number:06d}"
        )
