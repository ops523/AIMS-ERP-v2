import pandas as pd
import streamlit as st

from database import SessionLocal

from services.inventory_ledger_service import (
    InventoryLedgerService,
)

from components.page_header import PageHeader


PageHeader.render(

    "Inventory Ledger",

    "Inventory Movement History",

    "📚",

)

db = SessionLocal()

roll_id = st.number_input(

    "Roll ID",

    min_value=1,

)

if st.button("Load Ledger"):

    ledger = InventoryLedgerService.history(

        db,

        roll_id,

    )

    rows = []

    for tx in ledger:

        rows.append(

            {

                "Date": tx.transaction_date,

                "Module": tx.reference_module,

                "Type": tx.transaction_type,

                "Qty In": tx.qty_in,

                "Qty Out": tx.qty_out,

                "Balance": tx.balance_qty,

                "Remarks": tx.remarks,

            }

        )

    st.data_editor(

        pd.DataFrame(rows),

        use_container_width=True,

        disabled=True,

    )
