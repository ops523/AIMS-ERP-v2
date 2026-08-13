from __future__ import annotations

import streamlit as st

from core.startup import startup


# =========================================================
# STARTUP
# =========================================================

startup()


from database import get_session

from constants.status import MediaRollStatus

from services.media_roll_service import MediaRollService

from repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
)

from components.media_roll_summary_cards import (
    MediaRollSummaryCards,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.title("Media Roll Inventory")

st.caption(
    "Monitor media roll stock, status, inventory movements "
    "and roll history."
)


# =========================================================
# DATABASE
# =========================================================

db = get_session()


# =========================================================
# DASHBOARD
# =========================================================

try:

    MediaRollSummaryCards.render(db)

except Exception as exc:

    st.error(
        "Unable to load Media Roll dashboard."
    )

    st.exception(exc)

    db.close()

    st.stop()


# =========================================================
# STOCK QUANTITY SUMMARY
# =========================================================

st.divider()

st.subheader("Stock Summary")


try:

    rolls = MediaRollService.search(
        db=db,
        keyword=None,
    )

    total_sqft = sum(
        float(
            getattr(
                roll,
                "total_sqft",
                0,
            )
            or 0
        )
        for roll in rolls
    )

    available_sqft = sum(
        float(
            getattr(
                roll,
                "available_sqft",
                0,
            )
            or 0
        )
        for roll in rolls
    )

    consumed_sqft = sum(
        max(
            float(
                getattr(
                    roll,
                    "total_sqft",
                    0,
                )
                or 0
            )
            - float(
                getattr(
                    roll,
                    "available_sqft",
                    0,
                )
                or 0
            ),
            0,
        )
        for roll in rolls
    )

    damaged_sqft = sum(
        float(
            getattr(
                roll,
                "total_sqft",
                0,
            )
            or 0
        )
        for roll in rolls
        if roll.status
        == MediaRollStatus.DAMAGED
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Total Sq Ft",
            f"{total_sqft:,.2f}",
        )

    with c2:

        st.metric(
            "Available Sq Ft",
            f"{available_sqft:,.2f}",
        )

    with c3:

        st.metric(
            "Consumed / Used Sq Ft",
            f"{consumed_sqft:,.2f}",
        )

    with c4:

        st.metric(
            "Damaged Sq Ft",
            f"{damaged_sqft:,.2f}",
        )

except Exception as exc:

    st.error(
        "Unable to calculate stock summary."
    )

    st.exception(exc)


# =========================================================
# SEARCH
# =========================================================

st.divider()

st.subheader("Search Media Rolls")


search_col, status_col = st.columns(
    [2, 1]
)


with search_col:

    keyword = st.text_input(
        "Search",
        placeholder=(
            "Roll Number, Asset ID, Manufacturer Roll No., "
            "QR Payload, PO or Invoice"
        ),
    )


with status_col:

    status_options = [
        "ALL",
        MediaRollStatus.RECEIVED,
        MediaRollStatus.AVAILABLE,
        MediaRollStatus.RESERVED,
        MediaRollStatus.ALLOCATED,
        MediaRollStatus.PRINTING,
        MediaRollStatus.PRINTED,
        MediaRollStatus.PARTIALLY_USED,
        MediaRollStatus.CONSUMED,
        MediaRollStatus.RETURNED,
        MediaRollStatus.DAMAGED,
        MediaRollStatus.LOST,
    ]

    selected_status = st.selectbox(
        "Status",
        status_options,
    )


# =========================================================
# LOAD ROLLS
# =========================================================

try:

    filtered_rolls = MediaRollService.search(
        db=db,
        keyword=keyword.strip()
        if keyword
        else None,
    )

except Exception as exc:

    st.error(
        "Unable to search Media Rolls."
    )

    st.exception(exc)

    db.close()

    st.stop()


# =========================================================
# STATUS FILTER
# =========================================================

if selected_status != "ALL":

    filtered_rolls = [
        roll
        for roll in filtered_rolls
        if roll.status == selected_status
    ]


# =========================================================
# RESULT COUNT
# =========================================================

st.caption(
    f"{len(filtered_rolls)} Media Roll(s) found."
)


# =========================================================
# INVENTORY TABLE
# =========================================================

st.subheader("Roll Inventory")


table_rows = []


for roll in filtered_rolls:

    table_rows.append(
        {
            "ID": roll.id,
            "Roll Number": roll.roll_number,
            "Asset ID": roll.asset_id,
            "Manufacturer Roll No.": (
                roll.manufacturer_roll_no
                or ""
            ),
            "Status": roll.status,
            "Width (ft)": (
                round(
                    float(
                        roll.width_ft
                    ),
                    2,
                )
                if roll.width_ft is not None
                else None
            ),
            "Total Sq Ft": round(
                float(
                    roll.total_sqft
                    or 0
                ),
                2,
            ),
            "Available Sq Ft": round(
                float(
                    roll.available_sqft
                    or 0
                ),
                2,
            ),
            "Purchase Order": (
                roll.purchase_order
                or ""
            ),
            "Invoice": (
                roll.invoice_number
                or ""
            ),
        }
    )


if table_rows:

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No Media Rolls match the selected criteria."
    )


# =========================================================
# ROLL DETAILS
# =========================================================

if filtered_rolls:

    st.divider()

    st.subheader("Roll Details")

    roll_options = {
        (
            f"{roll.roll_number} — "
            f"{roll.asset_id}"
        ): roll
        for roll in filtered_rolls
    }

    selected_roll_label = st.selectbox(
        "Select a Media Roll",
        list(
            roll_options.keys()
        ),
    )

    selected_roll = roll_options[
        selected_roll_label
    ]


    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Status",
            selected_roll.status,
        )

    with c2:

        st.metric(
            "Total Sq Ft",
            f"{float(selected_roll.total_sqft or 0):,.2f}",
        )

    with c3:

        st.metric(
            "Available Sq Ft",
            f"{float(selected_roll.available_sqft or 0):,.2f}",
        )

    with c4:

        utilization = 0

        if selected_roll.total_sqft:

            utilization = (
                (
                    selected_roll.total_sqft
                    - selected_roll.available_sqft
                )
                / selected_roll.total_sqft
            ) * 100

        st.metric(
            "Used %",
            f"{utilization:.1f}%",
        )


    # -----------------------------------------------------
    # ROLL INFORMATION
    # -----------------------------------------------------

    st.markdown("### Roll Information")

    detail_rows = [
        {
            "Field": "Roll Number",
            "Value": selected_roll.roll_number,
        },
        {
            "Field": "Asset ID",
            "Value": selected_roll.asset_id,
        },
        {
            "Field": "Manufacturer Roll No.",
            "Value": (
                selected_roll.manufacturer_roll_no
                or ""
            ),
        },
        {
            "Field": "Width",
            "Value": (
                f"{selected_roll.width_ft} ft"
            ),
        },
        {
            "Field": "Ordered Length",
            "Value": (
                f"{selected_roll.ordered_length_m} m"
            ),
        },
        {
            "Field": "Actual Length",
            "Value": (
                f"{selected_roll.actual_length_m} m"
            ),
        },
        {
            "Field": "Purchase Order",
            "Value": (
                selected_roll.purchase_order
                or ""
            ),
        },
        {
            "Field": "Invoice",
            "Value": (
                selected_roll.invoice_number
                or ""
            ),
        },
        {
            "Field": "QR Payload",
            "Value": (
                selected_roll.qr_payload
                or ""
            ),
        },
        {
            "Field": "QR Image",
            "Value": (
                selected_roll.qr_image_path
                or ""
            ),
        },
    ]

    st.dataframe(
        detail_rows,
        use_container_width=True,
        hide_index=True,
    )


    # =====================================================
    # TABS
    # =====================================================

    history_tab, inventory_tab, qr_tab = st.tabs(
        [
            "Status History",
            "Inventory Transactions",
            "QR",
        ]
    )


    # -----------------------------------------------------
    # STATUS HISTORY
    # -----------------------------------------------------

    with history_tab:

        try:

            history = MediaRollService.history(
                db=db,
                media_roll_id=selected_roll.id,
            )

            history_rows = []

            for event in history:

                history_rows.append(
                    {
                        "Date": (
                            event.created_at
                        ),
                        "Event": (
                            event.event
                        ),
                        "Previous Status": (
                            event.previous_status
                            or ""
                        ),
                        "Current Status": (
                            event.current_status
                            or ""
                        ),
                        "Reference": (
                            event.reference_number
                            or ""
                        ),
                        "Remarks": (
                            event.remarks
                            or ""
                        ),
                        "Performed By": (
                            event.scanned_by
                            or ""
                        ),
                    }
                )

            if history_rows:

                st.dataframe(
                    history_rows,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No status history available."
                )

        except Exception as exc:

            st.error(
                "Unable to load status history."
            )

            st.exception(exc)


    # -----------------------------------------------------
    # INVENTORY TRANSACTIONS
    # -----------------------------------------------------

    with inventory_tab:

        try:

            transactions = (
                InventoryTransactionRepository.history(
                    db=db,
                    media_roll_id=selected_roll.id,
                )
            )

            transaction_rows = []

            for tx in transactions:

                transaction_rows.append(
                    {
                        "Date": (
                            tx.transaction_date
                        ),
                        "Transaction": (
                            tx.transaction_type
                        ),
                        "Qty In": round(
                            float(
                                tx.qty_in
                                or 0
                            ),
                            2,
                        ),
                        "Qty Out": round(
                            float(
                                tx.qty_out
                                or 0
                            ),
                            2,
                        ),
                        "Balance": round(
                            float(
                                tx.balance_qty
                                or 0
                            ),
                            2,
                        ),
                        "Wastage": round(
                            float(
                                tx.wastage_sqft
                                or 0
                            ),
                            2,
                        ),
                        "Module": (
                            tx.reference_module
                        ),
                        "Remarks": (
                            tx.remarks
                            or ""
                        ),
                        "Performed By": (
                            tx.performed_by
                            or ""
                        ),
                    }
                )

            if transaction_rows:

                st.dataframe(
                    transaction_rows,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No inventory transactions available."
                )

        except Exception as exc:

            st.error(
                "Unable to load inventory transactions."
            )

            st.exception(exc)


    # -----------------------------------------------------
    # QR
    # -----------------------------------------------------

    with qr_tab:

        st.markdown("### QR Information")

        if selected_roll.qr_payload:

            st.code(
                selected_roll.qr_payload,
                language=None,
            )

        else:

            st.warning(
                "QR payload has not been generated."
            )

        if selected_roll.qr_image_path:

            st.caption(
                "QR image path:"
            )

            st.code(
                selected_roll.qr_image_path,
                language=None,
            )

            try:

                st.image(
                    selected_roll.qr_image_path,
                    width=250,
                )

            except Exception:

                st.info(
                    "QR image file could not be displayed."
                )

        else:

            st.info(
                "No QR image is currently associated "
                "with this Media Roll."
            )


# =========================================================
# CLOSE DATABASE
# =========================================================

db.close()
