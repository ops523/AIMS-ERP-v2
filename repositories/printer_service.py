from sqlalchemy.orm import Session

from models.printer import Printer


class PrinterService:

    @staticmethod
    def create(
        db: Session,
        code: str,
        name: str,
        capacity: float,
        night_capacity: float,
    ):

        printer = Printer(
            printer_code=code,
            printer_name=name,
            print_capacity_day=capacity,
            night_shift_capacity=night_capacity,
        )

        db.add(printer)
        db.commit()
        db.refresh(printer)

        return printer
