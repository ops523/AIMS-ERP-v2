from sqlalchemy.orm import Session

from models.printer import Printer
from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.warehouse import Warehouse
from models.media_product import MediaProduct
from models.user import User

from models.document_sequence import DocumentSequence
from models.system_setting import SystemSetting

from utils.security import hash_password


def seed_database(db: Session):

    # ==========================================================
    # PRINTERS
    # ==========================================================

    if db.query(Printer).count() == 0:

        db.add_all([

            Printer(
                printer_code="PR001",
                printer_name="SMK Printing",
                city="Mumbai",
                state="Maharashtra",
                print_capacity_day=7500,
                night_shift_capacity=15000,
                is_active=True,
            ),

            Printer(
                printer_code="PR002",
                printer_name="Beta Printers",
                city="Mumbai",
                state="Maharashtra",
                print_capacity_day=15000,
                night_shift_capacity=30000,
                is_active=True,
            ),

        ])

    # ==========================================================
    # WAREHOUSE
    # ==========================================================

    if db.query(Warehouse).count() == 0:

        db.add(

            Warehouse(
                warehouse_code="WH001",
                warehouse_name="Central Warehouse",
                city="Delhi",
                state="Delhi",
                is_active=True,
            )

        )

    # ==========================================================
    # MANUFACTURER
    # ==========================================================

    manufacturer = db.query(Manufacturer).first()

    if manufacturer is None:

        manufacturer = Manufacturer(

            manufacturer_code="MF001",
            manufacturer_name="Demo Manufacturer",
            country="India",
            website="",
            is_active=True,

        )

        db.add(manufacturer)
        db.commit()
        db.refresh(manufacturer)

    # ==========================================================
    # SUPPLIER
    # ==========================================================

    if db.query(Supplier).count() == 0:

        db.add(

            Supplier(
                supplier_code="SUP001",
                supplier_name="Demo Supplier",
                contact_person="",
                mobile="",
                email="",
                gst_number="",
                address="",
                city="Delhi",
                state="Delhi",
                pincode="110001",
                is_active=True,
            )

        )

    # ==========================================================
    # MEDIA PRODUCT
    # ==========================================================

    if db.query(MediaProduct).count() == 0:

        db.add(

            MediaProduct(
                product_code="MP001",
                manufacturer_id=manufacturer.id,
                product_name="Digital Wall Painting Media",
                width_ft=4.0,
                gsm=300,
                finish="Matte",
                standard_length_m=95,
                is_active=True,
            )

        )

    # ==========================================================
    # ADMIN USER
    # ==========================================================

    if db.query(User).count() == 0:

        db.add(

            User(
                username="admin",
                password_hash=hash_password("admin@123"),
                full_name="Administrator",
                role="Admin",
                is_active=True,
            )

        )

    # ==========================================================
    # DOCUMENT SEQUENCES
    # ==========================================================

    if db.query(DocumentSequence).count() == 0:

        db.add_all([

            DocumentSequence(
                document_type="CAMPAIGN",
                prefix="CMP",
                last_number=0,
            ),

            DocumentSequence(
                document_type="CAMPAIGN_VERSION",
                prefix="CV",
                last_number=0,
            ),

            DocumentSequence(
                document_type="PRODUCTION_BATCH",
                prefix="PB",
                last_number=0,
            ),

            DocumentSequence(
                document_type="PRINTING_SESSION",
                prefix="PS",
                last_number=0,
            ),

            DocumentSequence(
                document_type="MEDIA_ROLL",
                prefix="MR",
                last_number=0,
            ),

            DocumentSequence(
                document_type="PACKAGE",
                prefix="PK",
                last_number=0,
            ),

            DocumentSequence(
                document_type="DISPATCH",
                prefix="DS",
                last_number=0,
            ),

            DocumentSequence(
                document_type="INVENTORY_TRANSACTION",
                prefix="IT",
                last_number=0,
            ),

            DocumentSequence(
                document_type="PURCHASE_ORDER",
                prefix="PO",
                last_number=0,
            ),

            DocumentSequence(
                document_type="WAREHOUSE_TRANSFER",
                prefix="WT",
                last_number=0,
            ),

        ])

        db.commit()
    # ==========================================================
    # SYSTEM SETTINGS
    # ==========================================================

    if db.query(SystemSetting).count() == 0:

        db.add_all([

            SystemSetting(
                setting_key="DEFAULT_ROLL_SIZE",
                setting_value="1250",
                description="Default printable sqft per media roll",
            ),

            SystemSetting(
                setting_key="PRINT_WASTAGE_PERCENT",
                setting_value="12",
                description="Default print wastage percentage",
            ),

            SystemSetting(
                setting_key="GUM_PER_1000_SQFT",
                setting_value="5",
                description="Kg of gum required per 1000 sqft",
            ),

            SystemSetting(
                setting_key="TRANSIT_DAYS",
                setting_value="2",
                description="Average dispatch transit days",
            ),

            SystemSetting(
                setting_key="NIGHT_SHIFT_MULTIPLIER",
                setting_value="2",
                description="Night shift production multiplier",
            ),

            SystemSetting(
                setting_key="QR_PREFIX",
                setting_value="ADW",
                description="Prefix for QR codes",
            ),

        ])

    # ==========================================================
    # SAVE
    # ==========================================================

    db.commit()
