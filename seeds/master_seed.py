from database import get_session
from models.printer import Printer

db = get_session()

printers = [
    Printer(
        printer_code="SMK",
        printer_name="SMK Printing",
        print_capacity_day=7500,
        night_shift_capacity=15000,
    ),
    Printer(
        printer_code="BETA",
        printer_name="Beta Printers",
        print_capacity_day=15000,
        night_shift_capacity=30000,
    ),
]

for printer in printers:
    exists = (
        db.query(Printer)
        .filter(Printer.printer_code == printer.printer_code)
        .first()
    )
    if not exists:
        db.add(printer)

db.commit()
db.close()
