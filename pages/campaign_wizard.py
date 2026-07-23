import streamlit as st
import pandas as pd

from services.excel_validation_service import (
    ExcelValidationService,
)

st.title("Campaign Import Wizard")

st.subheader("Step 1 : Upload Campaign Excel")

uploaded_file = st.file_uploader(
    "Select Campaign Excel",
    type=["xlsx", "xls"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    valid, errors = ExcelValidationService.validate(df)

    if not valid:

        st.error("Validation Failed")

        for err in errors:

            st.write("•", err)

    else:

        st.success("Excel Validated Successfully")

        st.dataframe(df)
