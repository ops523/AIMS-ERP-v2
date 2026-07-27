import streamlit as st

from database import get_session
from repositories.campaign_repository import CampaignRepository


class StepCampaign:

    @staticmethod
    def render():

        db = get_session()

        campaigns = CampaignRepository.get_all(db)

        st.markdown("### Step 1 : Select Campaign")

        if not campaigns:

            st.warning("No Campaigns available.")

            db.close()

            return

        options = {
            c.campaign_name: c.id
            for c in campaigns
        }

        selected = st.selectbox(
            "Campaign",
            list(options.keys()),
        )

        if st.button(
            "Next ➜",
            type="primary",
        ):

            st.session_state.selected_campaign = options[selected]

            st.session_state.wizard_step = 2

            st.rerun()

        db.close()
