from __future__ import annotations

import uuid

import pandas as pd
import streamlit as st

from core.startup import startup

startup()

from database import get_session

from models.campaign import Campaign
from models.campaign_version import CampaignVersion

from utils.enums import Priority

from services.campaign_service import CampaignService
from services.campaign_import_service import CampaignImportService
from services.excel_validation_service import ExcelValidationService

from components.aggrid_table import AgGridTable


st.title("📦 Campaign Import Wizard")

db = get_session()


# ============================================================
# CAMPAIGN DETAILS
# ============================================================

st.subheader("Step 1 : Campaign Details")

col1, col2 = st.columns(2)

with col1:

    client = st.text_input("Client")

    brand = st.text_input("Brand")

    campaign_name = st.text_input(
        "Campaign Name"
    )

    agency = st.text_input("Agency")


with col2:

    campaign_type = st.text_input(
        "Campaign Type"
    )

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

    start_date = st.date_input(
        "Start Date"
    )

    end_date = st.date_input(
        "End Date"
    )


remarks = st.text_area("Remarks")


st.divider()


# ============================================================
# EXCEL UPLOAD
# ============================================================

st.subheader("Step 2 : Upload Campaign Excel")

uploaded_file = st.file_uploader(
    "Upload Campaign Excel",
    type=["xlsx", "xls"],
)


if uploaded_file is not None:

    df = pd.read_excel(
        uploaded_file
    )

    valid, errors = (
        ExcelValidationService.validate(df)
    )

    if not valid:

        st.error(
            "Validation Failed"
        )

        for err in errors:

            st.write(
                f"• {err}"
            )

        st.stop()


    st.success(
        "Excel Validation Successful"
    )


    # --------------------------------------------------------
    # EDITABLE GRID
    # --------------------------------------------------------

    response = AgGridTable.editable(
        df
    )

    edited_df = response["data"].copy()

    st.session_state[
        "campaign_df"
    ] = edited_df


    # --------------------------------------------------------
    # CALCULATIONS
    # --------------------------------------------------------

    edited_df["Wall Sq Ft"] = (
        edited_df["Wall Width (ft)"]
        * edited_df["Wall Height (ft)"]
    )

    edited_df["Total Sq Ft"] = (
        edited_df["Wall Sq Ft"]
        * edited_df["Qty"]
    )


    total_locations = len(
        edited_df
    )

    total_walls = int(
        edited_df["Qty"].sum()
    )

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


    # ========================================================
    # CREATE CAMPAIGN
    # ========================================================

    if st.button(
        "🚀 Create Campaign",
        type="primary",
        use_container_width=True,
    ):

        # ----------------------------------------------------
        # REQUIRED CAMPAIGN FIELDS
        # ----------------------------------------------------

        if not client.strip():

            st.error(
                "Client is required."
            )

            st.stop()


        if not brand.strip():

            st.error(
                "Brand is required."
            )

            st.stop()


        if not campaign_name.strip():

            st.error(
                "Campaign Name is required."
            )

            st.stop()


        if end_date < start_date:

            st.error(
                "End Date cannot be before Start Date."
            )

            st.stop()


        try:

            # ------------------------------------------------
            # 1. BUILD CAMPAIGN
            # ------------------------------------------------

            campaign = Campaign(

                client_name=client.strip(),

                brand_name=brand.strip(),

                campaign_name=campaign_name.strip(),

                agency_name=agency.strip(),

                campaign_type=campaign_type.strip(),

                priority=priority,

                start_date=start_date,

                end_date=end_date,

                remarks=remarks.strip(),

            )


            # ------------------------------------------------
            # 2. BUILD VERSION
            # ------------------------------------------------
            #
            # campaign_id is intentionally left unset.
            # CampaignService assigns it after creating
            # the Campaign record.
            #
            # import_batch MUST be unique.
            # ------------------------------------------------

            import_batch = (
                f"IMP-{uuid.uuid4().hex[:12].upper()}"
            )

            version = CampaignVersion(

                version_no=1,

                version_name="V1",

                import_batch=import_batch,

                total_locations=total_locations,

                total_walls=total_walls,

                total_sqft=total_sqft,

            )


            # ------------------------------------------------
            # 3. BUILD LOCATIONS
            # ------------------------------------------------
            #
            # version_id is intentionally None.
            # CampaignService assigns the CampaignVersion
            # relationship before persistence.
            # ------------------------------------------------

            locations = (
                CampaignImportService.create_locations(
                    df=edited_df,
                    version_id=None,
                )
            )


            # ------------------------------------------------
            # 4. ARTWORKS
            # ------------------------------------------------
            #
            # The current campaign Excel contains location/
            # wall information, not actual artwork information.
            #
            # Therefore we DO NOT create fake artwork records.
            #
            # Artwork management will be handled separately.
            # ------------------------------------------------

            artworks = []


            # ------------------------------------------------
            # 5. ATOMIC CAMPAIGN CREATION
            # ------------------------------------------------
            #
            # CampaignService now owns:
            #
            # Campaign
            #     ↓
            # CampaignVersion
            #     ↓
            # Artworks
            #     ↓
            # Locations
            #     ↓
            # COMMIT
            # ------------------------------------------------

            campaign, version = (
                CampaignService.create_campaign(
                    db=db,
                    campaign=campaign,
                    version=version,
                    artworks=artworks,
                    locations=locations,
                )
            )


            # ------------------------------------------------
            # 6. SUCCESS
            # ------------------------------------------------

            st.success(
                f"Campaign "
                f"{campaign.campaign_code} "
                f"created successfully."
            )

            st.balloons()


            st.info(
                f"""
Campaign Code : {campaign.campaign_code}

Version : {version.version_name}

Import Batch : {version.import_batch}

Locations : {version.total_locations}

Walls : {version.total_walls}

Sq Ft : {version.total_sqft:,.2f}
"""
            )


            # ------------------------------------------------
            # CLEAR OLD WIZARD DATA
            # ------------------------------------------------

            st.session_state.pop(
                "campaign_df",
                None,
            )


        except Exception as exc:

            db.rollback()

            st.error(
                "Unable to create campaign."
            )

            st.exception(
                exc
            )

db.close()