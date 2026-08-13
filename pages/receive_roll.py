from __future__ import annotations

import streamlit as st

from core.startup import startup

startup()

from database import get_session

from models.media_roll import MediaRoll

from repositories.supplier_repository import (
    SupplierRepository,
)

from repositories.manufacturer_repository import (
    ManufacturerRepository,
)

from repositories.warehouse_repository import (
    WarehouseRepository,
)

from repositories.media_product_repository import (
    MediaProductRepository,
)

from services.media_roll_service import (
    MediaRollService,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.title("Receive Media Rolls")

st.caption(
    "Receive physical media rolls into warehouse inventory."
)


# =========================================================
# DATABASE
# =========================================================

db = get_session()


# =========================================================
# LOAD MASTER DATA
# =========================================================

try:

    suppliers = SupplierRepository.get_all(db)

    manufacturers = ManufacturerRepository.get_all(db)

    warehouses = WarehouseRepository.get_all(db)

    products = MediaProductRepository.get_all(db)

except Exception as exc:

    st.error(
        "Unable to load master data."
    )

    st.exception(exc)

    db.close()

    st.stop()


# =========================================================
# MASTER DATA VALIDATION
# =========================================================

if not suppliers:

    st.warning(
        "No active suppliers are available. "
        "Please create a supplier before receiving media rolls."
    )

    db.close()

    st.stop()


if not manufacturers:

    st.warning(
        "No active manufacturers are available. "
        "Please create a manufacturer before receiving media rolls."
    )

    db.close()

    st.stop()


if not warehouses:

    st.warning(
        "No active warehouses are available. "
        "Please create a warehouse before receiving media rolls."
    )

    db.close()

    st.stop()


if not products:

    st.warning(
        "No active media products are available. "
        "Please create a media product before receiving rolls."
    )

    db.close()

    st.stop()


# =========================================================
# COMMON RECEIPT INFORMATION
# =========================================================

st.subheader("Receipt Information")

c1, c2 = st.columns(2)


with c1:

    supplier = st.selectbox(
        "Supplier",
        suppliers,
        format_func=lambda x: (
            f"{x.supplier_code} — "
            f"{x.supplier_name}"
        ),
    )


with c2:

    manufacturer = st.selectbox(
        "Manufacturer",
        manufacturers,
        format_func=lambda x: (
            f"{x.manufacturer_code} — "
            f"{x.manufacturer_name}"
        ),
    )


c3, c4 = st.columns(2)


with c3:

    warehouse = st.selectbox(
        "Warehouse",
        warehouses,
        format_func=lambda x: (
            f"{x.warehouse_code} — "
            f"{x.warehouse_name}"
        ),
    )


with c4:

    product = st.selectbox(
        "Media Product",
        products,
        format_func=lambda x: (
            f"{x.product_code} — "
            f"{x.product_name}"
        ),
    )


c5, c6 = st.columns(2)


with c5:

    purchase_order = st.text_input(
        "Purchase Order",
        placeholder="PO-0001",
    )


with c6:

    invoice_number = st.text_input(
        "Invoice Number",
        placeholder="INV-0001",
    )


c7, c8 = st.columns(2)


with c7:

    invoice_date = st.date_input(
        "Invoice Date",
    )


with c8:

    number_of_rolls = st.number_input(
        "Number of Rolls",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
    )


# =========================================================
# PRODUCT INFORMATION
# =========================================================

st.divider()

st.subheader("Selected Media Product")

pc1, pc2, pc3, pc4 = st.columns(4)


with pc1:

    st.metric(
        "Product",
        product.product_name,
    )


with pc2:

    st.metric(
        "Standard Width",
        f"{product.width_ft:g} ft",
    )


with pc3:

    if product.standard_length_m:

        st.metric(
            "Standard Length",
            f"{product.standard_length_m:g} m",
        )

    else:

        st.metric(
            "Standard Length",
            "Not Set",
        )


with pc4:

    if product.gsm is not None:

        st.metric(
            "GSM",
            f"{product.gsm:g}",
        )

    else:

        st.metric(
            "GSM",
            "Not Set",
        )


# =========================================================
# ROLL DETAILS
# =========================================================

st.divider()

st.subheader("Roll Details")

st.info(
    "Enter the physical details for each roll. "
    "Each roll will receive its own Asset ID, "
    "Roll Number, QR code, inventory transaction "
    "and history."
)


# =========================================================
# DEFAULT VALUES
# =========================================================

default_length = (
    float(product.standard_length_m)
    if product.standard_length_m
    else 50.0
)

default_width = (
    float(product.width_ft)
    if product.width_ft
    else 4.0
)


if default_width not in (4.0, 5.0):

    default_width = 4.0


default_rows = []

for index in range(int(number_of_rolls)):

    default_rows.append(
        {
            "Manufacturer Roll No.": "",
            "Ordered Length (m)": default_length,
            "Actual Length (m)": default_length,
            "Width (ft)": default_width,
        }
    )


# =========================================================
# ROLL DATA EDITOR
# =========================================================

roll_data = st.data_editor(
    default_rows,
    key="receive_roll_editor",
    num_rows="fixed",
    use_container_width=True,
    hide_index=False,
    column_config={
        "Manufacturer Roll No.": st.column_config.TextColumn(
            "Manufacturer Roll No.",
            help=(
                "Physical roll number printed or supplied "
                "by the manufacturer."
            ),
            required=False,
        ),
        "Ordered Length (m)": st.column_config.NumberColumn(
            "Ordered Length (m)",
            min_value=0.01,
            step=0.1,
            format="%.2f",
        ),
        "Actual Length (m)": st.column_config.NumberColumn(
            "Actual Length (m)",
            min_value=0.01,
            step=0.1,
            format="%.2f",
        ),
        "Width (ft)": st.column_config.SelectboxColumn(
            "Width (ft)",
            options=[4.0, 5.0],
            required=True,
        ),
    },
)


# =========================================================
# ROLL PREVIEW
# =========================================================

st.divider()

st.subheader("Receipt Preview")

preview_rows = []

for index, row in enumerate(roll_data):
    roll_position = index + 1
    
    try:

        actual_length = float(
            row["Actual Length (m)"]
        )

        width_ft = float(
            row["Width (ft)"]
        )

        total_sqft = (
            actual_length
            * 3.28084
            * width_ft
        )

    except (
        TypeError,
        ValueError,
    ):

        total_sqft = 0.0

    preview_rows.append(
        {
            "Roll": index + 1,
            "Manufacturer Roll No.": (
                row["Manufacturer Roll No."]
            ),
            "Actual Length (m)": (
                row["Actual Length (m)"]
            ),
            "Width (ft)": width_ft,
            "Calculated Sq Ft": round(
                total_sqft,
                2,
            ),
        }
    )


st.dataframe(
    preview_rows,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# TOTAL RECEIPT SUMMARY
# =========================================================

total_receipt_sqft = sum(
    row["Calculated Sq Ft"]
    for row in preview_rows
)


sc1, sc2, sc3 = st.columns(3)


with sc1:

    st.metric(
        "Total Rolls",
        len(preview_rows),
    )


with sc2:

    st.metric(
        "Total Sq Ft",
        f"{total_receipt_sqft:,.2f}",
    )


with sc3:

    st.metric(
        "Warehouse",
        warehouse.warehouse_name,
    )


# =========================================================
# RECEIVING USER
# =========================================================

st.divider()

remarks = st.text_area(
    "Remarks",
    placeholder=(
        "Optional remarks about this receipt..."
    ),
)


# =========================================================
# RECEIVE BUTTON
# =========================================================

receive_clicked = st.button(
    "Receive Media Rolls",
    type="primary",
    use_container_width=True,
)


# =========================================================
# RECEIVE TRANSACTION
# =========================================================

if receive_clicked:

    validation_errors = []

    # -----------------------------------------------------
    # Header validation
    # -----------------------------------------------------

    if supplier is None:

        validation_errors.append(
            "Supplier is required."
        )

    if manufacturer is None:

        validation_errors.append(
            "Manufacturer is required."
        )

    if warehouse is None:

        validation_errors.append(
            "Warehouse is required."
        )

    if product is None:

        validation_errors.append(
            "Media Product is required."
        )

    # -----------------------------------------------------
    # Roll validation
    # -----------------------------------------------------

    for index, row in enumerate(roll_data):
        roll_position = index + 1
        
        manufacturer_roll_no = str(
            row["Manufacturer Roll No."]
        ).strip()

        if not manufacturer_roll_no:

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Manufacturer Roll No. is required."
                )
            )

        try:

            ordered_length = float(
                row["Ordered Length (m)"]
            )

        except (
            TypeError,
            ValueError,
        ):

            ordered_length = 0

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Ordered Length must be a valid number."
                )
            )

        try:

            actual_length = float(
                row["Actual Length (m)"]
            )

        except (
            TypeError,
            ValueError,
        ):

            actual_length = 0

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Actual Length must be a valid number."
                )
            )

        try:

            width_ft = float(
                row["Width (ft)"]
            )

        except (
            TypeError,
            ValueError,
        ):

            width_ft = 0

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Width must be valid."
                )
            )

        if ordered_length <= 0:

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Ordered Length must be greater than zero."
                )
            )

        if actual_length <= 0:

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Actual Length must be greater than zero."
                )
            )

        if width_ft not in (4.0, 5.0):

            validation_errors.append(
                (
                    f"Roll {roll_number_display}: "
                    "Width must be either 4 ft or 5 ft."
                )
            )

    # -----------------------------------------------------
    # Display validation errors
    # -----------------------------------------------------

    if validation_errors:

        st.error(
            "Please correct the following errors:"
        )

        for error in validation_errors:

            st.write(
                f"• {error}"
            )

        db.close()

        st.stop()


    # =====================================================
    # PROCESS EACH ROLL
    # =====================================================

    user = (
        st.session_state.get(
            "username"
        )
        or st.session_state.get(
            "user"
        )
        or "STREAMLIT_USER"
    )


    successful_rolls = []

    failed_rolls = []


    progress = st.progress(
        0
    )


    status_text = st.empty()


    total_rolls = len(
        roll_data
    )


    for index, row in enumerate(roll_data):
        roll_position = index + 1
        
        status_text.info(
            (
                f"Receiving roll "
                f"{roll_position} of "
                f"{total_rolls}..."
            )
        )


        manufacturer_roll_no = str(
            row["Manufacturer Roll No."]
        ).strip()


        ordered_length = float(
            row["Ordered Length (m)"]
        )


        actual_length = float(
            row["Actual Length (m)"]
        )


        width_ft = float(
            row["Width (ft)"]
        )


        # -------------------------------------------------
        # Calculate actual physical area
        # -------------------------------------------------

        total_sqft = (
            actual_length
            * 3.28084
            * width_ft
        )


        # -------------------------------------------------
        # Build MediaRoll business object
        # -------------------------------------------------

        media_roll = MediaRoll(

            supplier_id=supplier.id,

            manufacturer_id=manufacturer.id,

            product_id=product.id,

            warehouse_id=warehouse.id,

            manufacturer_roll_no=(
                manufacturer_roll_no
            ),

            purchase_order=(
                purchase_order.strip()
                or None
            ),

            invoice_number=(
                invoice_number.strip()
                or None
            ),

            invoice_date=invoice_date,

            ordered_length_m=(
                ordered_length
            ),

            actual_length_m=(
                actual_length
            ),

            width_ft=width_ft,

            total_sqft=total_sqft,

            available_sqft=total_sqft,

            remarks=(
                remarks.strip()
                or None
            ),

        )


        # -------------------------------------------------
        # Business transaction
        # -------------------------------------------------

        result = MediaRollService.receive(
            db=db,
            media_roll=media_roll,
            user=user,
        )


        # -------------------------------------------------
        # Result handling
        # -------------------------------------------------

        if result.success:

            received_roll = result.data

            successful_rolls.append(
                received_roll
            )

        else:

            failed_rolls.append(
                {
                    "roll": roll_position,
                    "manufacturer_roll_no": (
                        manufacturer_roll_no
                    ),
                    "message": result.message,
                    "errors": result.errors or [],
                }
            )


        progress.progress(
            roll_position / total_rolls
        )


    status_text.empty()


    # =====================================================
    # SUCCESS SUMMARY
    # =====================================================

    if successful_rolls:

        st.success(
            (
                f"{len(successful_rolls)} "
                "Media Roll(s) received successfully."
            )
        )


        st.subheader(
            "Received Rolls"
        )


        success_rows = []


        for received_roll in successful_rolls:

            success_rows.append(
                {
                    "Roll Number": (
                        received_roll.roll_number
                    ),
                    "Asset ID": (
                        received_roll.asset_id
                    ),
                    "Manufacturer Roll No.": (
                        received_roll.manufacturer_roll_no
                    ),
                    "Status": (
                        received_roll.status
                    ),
                    "Total Sq Ft": round(
                        received_roll.total_sqft,
                        2,
                    ),
                    "QR": (
                        "Generated"
                        if received_roll.qr_image_path
                        else "Not Generated"
                    ),
                }
            )


        st.dataframe(
            success_rows,
            use_container_width=True,
            hide_index=True,
        )


    # =====================================================
    # FAILED ROLLS
    # =====================================================

    if failed_rolls:

        st.error(
            (
                f"{len(failed_rolls)} "
                "Roll(s) could not be received."
            )
        )


        for failed in failed_rolls:

            with st.expander(
                (
                    f"Roll {failed['roll']} — "
                    f"{failed['manufacturer_roll_no']}"
                )
            ):

                st.write(
                    failed["message"]
                )

                for error in failed["errors"]:

                    st.write(
                        f"• {error}"
                    )


    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    if successful_rolls and not failed_rolls:

        st.info(
            "All rolls have been received into inventory. "
            "Each roll has its own Asset ID, Roll Number, "
            "QR code, inventory transaction and history."
        )


    elif successful_rolls and failed_rolls:

        st.warning(
            (
                "Some rolls were received successfully "
                "while others failed. Each roll is processed "
                "as an independent business transaction."
            )
        )


    else:

        st.error(
            "No rolls were received."
        )


# =========================================================
# CLEANUP
# =========================================================

db.close()
