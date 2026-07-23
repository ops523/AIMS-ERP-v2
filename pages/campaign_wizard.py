import pandas as pd
import streamlit as st

from database import get_session

from models.campaign import Campaign
from utils.enums import Priority

from services.campaign_service import CampaignService
from services.campaign_import_service import CampaignImportService
from services.excel_validation_service import ExcelValidationService

from components.aggrid_table import AgGridTable


st.set_page_config(page_title="Campaign Import Wizard", layout="wide")

st.title("📦 Campaign Import Wizard")

db = get_session()

# ---------------------------------------------------
# Campaign Details
# ---------------------------------------------------

st.subheader("Step 1 : Campaign Details")

col1, col2 = st.columns(2)

with col1:

    client = st.text_input("Client")

    brand = st.text_input("Brand")

    campaign_name = st.text_input("Campaign Name")

    agency = st.text_input("Agency")

with col2:

    campaign_type = st.text_input("Campaign Type")

    priority = st.selectbox(
        "Priority",
        [
            Priority.LOW,
            Priority.MEDIUM,
            Priority.HIGH,
            Priority.URGENT,
        ],
        format_func=lambda x: x.value,
    )

    start_date = st.date_input("Start Date")

    end_date = st.date_input("End Date")

remarks = st.text_area("Remarks")

st.divider()

# ---------------------------------------------------
# Upload Excel
# ---------------------------------------------------

st.subheader("Step 2 : Upload Campaign Excel")

uploaded_file = st.file_uploader(
    "Upload Campaign Excel",
    type=["xlsx", "xls"],
)

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    valid, errors = ExcelValidationService.validate(df)

    if not valid:

        st.error("Validation Failed")

        for err in errors:
            st.write(f"• {err}")

        st.stop()

    st.success("Excel Validation Successful")

    # --------------------------------------------
    # Editable Grid
    # --------------------------------------------

    response = AgGridTable.editable(df)

    edited_df = response["data"].copy()

    st.session_state["campaign_df"] = edited_df

    # --------------------------------------------
    # Calculations
    # --------------------------------------------

    edited_df["Wall Sq Ft"] = (
        edited_df["Wall Width (ft)"]
        * edited_df["Wall Height (ft)"]
    )

    edited_df["Total Sq Ft"] = (
        edited_df["Wall Sq Ft"]
        * edited_df["Qty"]
    )

    total_locations = len(edited_df)

    total_walls = int(edited_df["Qty"].sum())

    total_sqft = round(
        edited_df["Total Sq Ft"].sum(),
        2,
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Locations",
        total_locations,
    )

    c2.metric(
        "Walls",
        total_walls,
    )

    c3.metric(
        "Total Sq Ft",
        total_sqft,
    )

    st.divider()

    # --------------------------------------------
    # Create Campaign
    # --------------------------------------------

    if st.button(
        "🚀 Create Campaign",
        type="primary",
        use_container_width=True,
    ):

        if client.strip() == "":
            st.error("Client is required.")
            st.stop()

        if brand.strip() == "":
            st.error("Brand is required.")
            st.stop()

        if campaign_name.strip() == "":
            st.error("Campaign Name is required.")
            st.stop()

        try:

            campaign = Campaign(

                client_name=client,

                brand_name=brand,

                campaign_name=campaign_name,

                agency_name=agency,

                campaign_type=campaign_type,

                priority=priority,

                start_date=start_date,

                end_date=end_date,

                remarks=remarks,

            )

            campaign, version = CampaignService.create_campaign(
                db,
                campaign,
            )

            locations = CampaignImportService.create_locations(
                version.id,
                edited_df,
            )

            db.add_all(locations)

            version.total_locations = len(locations)

            version.total_walls = int(
                edited_df["Qty"].sum()
            )

            version.total_sqft = float(
                edited_df["Total Sq Ft"].sum()
            )

            db.commit()

            st.success(
                f"Campaign {campaign.campaign_code} created successfully."
            )

            st.balloons()

            st.info(
                f"""
Campaign Code : {campaign.campaign_code}

Version : {version.version_name}

Locations : {version.total_locations}

Walls : {version.total_walls}

Sq Ft : {version.total_sqft:,.2f}
"""
            )

        except Exception as e:

            db.rollback()

            st.exception(e)
