import streamlit as st

from database import SessionLocal
from repositories.campaign_repository import CampaignRepository


def render():

    db = SessionLocal()

    try:

        campaigns = CampaignRepository.get_all(db)

        if not campaigns:
            st.warning("No campaigns available.")
            return

        options = {
            f"{c.campaign_code} - {c.campaign_name}": c
            for c in campaigns
        }

        selected = st.selectbox(
            "Select Campaign",
            list(options.keys()),
        )

        campaign = options[selected]

        st.session_state.selected_campaign = campaign

        st.write(f"**Client:** {campaign.client_name}")
        st.write(f"**Brand:** {campaign.brand_name}")
        st.write(f"**Start:** {campaign.start_date}")
        st.write(f"**End:** {campaign.end_date}")

    finally:
        db.close()

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col2:
        if st.button("Next ➜"):
            st.session_state.production_step = 2
            st.rerun()
