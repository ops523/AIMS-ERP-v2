from sqlalchemy.orm import Session

from models.printer import Printer


class PrinterRepository:

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(Printer)
            .filter(Printer.is_active == True)
            .order_by(Printer.printer_name)
            .all()
        )

    @staticmethod
    def create(db: Session, printer: Printer):

        db.add(printer)
        db.commit()
        db.refresh(printer)

        return printer
