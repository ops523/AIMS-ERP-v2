import streamlit as st

from database import get_session
from repositories.campaign_version_repository import (
    CampaignVersionRepository,
)


class StepVersion:

    @staticmethod
    def render():

        db = get_session()

        versions = (
            CampaignVersionRepository.get_by_campaign(
                db,
                st.session_state.selected_campaign,
            )
        )

        st.markdown("### Step 2 : Campaign Version")

        if not versions:

            st.warning("No versions found.")

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 1

                st.rerun()

            db.close()

            return

        options = {
            v.version_name: v.id
            for v in versions
        }

        selected = st.selectbox(
            "Version",
            list(options.keys()),
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 1

                st.rerun()

        with c2:

            if st.button(
                "Next ➜",
                type="primary",
            ):

                st.session_state.selected_version = options[selected]

                st.session_state.wizard_step = 3

                st.rerun()

        db.close()
