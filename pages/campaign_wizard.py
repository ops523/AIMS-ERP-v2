import pandas as pd
import streamlit as st

from database import get_session
from models.campaign import Campaign
from services.campaign_service import CampaignService
from services.campaign_import_service import CampaignImportService
from services.excel_validation_service import ExcelValidationService

st.title("Campaign Import Wizard")

db = get_session()

st.header("Step 1 - Campaign Details")

col1, col2 = st.columns(2)

with col1:

    client = st.text_input("Client")

    brand = st.text_input("Brand")

    campaign_name = st.text_input("Campaign Name")

    agency = st.text_input("Agency")

with col2:

    campaign_type = st.text_input("Campaign Type")

    start_date = st.date_input("Start Date")

    end_date = st.date_input("End Date")

    priority = st.selectbox(

        "Priority",

        [

            "LOW",

            "MEDIUM",

            "HIGH",

            "URGENT"

        ]

    )

remarks = st.text_area("Remarks")

st.divider()

uploaded = st.file_uploader(

    "Campaign Excel",

    type=["xlsx", "xls"]

)

if uploaded:

    df = pd.read_excel(uploaded)

    valid, errors = ExcelValidationService.validate(df)

    if valid:

        st.success("Excel validated.")

        st.dataframe(df, use_container_width=True)

        if st.button("Create Campaign"):

            campaign = Campaign(

                client_name=client,

                brand_name=brand,

                campaign_name=campaign_name,

                agency_name=agency,

                campaign_type=campaign_type,

                priority=priority,

                start_date=start_date,

                end_date=end_date,

                remarks=remarks

            )

            campaign, version = CampaignService.create_campaign(

                db,

                campaign

            )

            locations = CampaignImportService.create_locations(

                version.id,

                df

            )

            db.add_all(locations)

            db.commit()

            st.success(

                f"Campaign {campaign.campaign_code} created successfully."

            )

            st.balloons()

    else:

        st.error("Validation Failed")

        for err in errors:

            st.write(err)
