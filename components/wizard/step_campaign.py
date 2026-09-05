from __future__ import annotations

import streamlit as st

from database import get_session
from repositories.campaign_repository import CampaignRepository


# Session-state keys that belong to later wizard steps.
DOWNSTREAM_KEYS = (
    "selected_version",
    "selected_artworks",
    "artwork_quantities",
    "total_planned_sqft",
    "selected_printer",
    "selected_shift",
    "printer_capacity",
)


def _clear_downstream_state() -> None:
    """Clear selections that are no longer valid after campaign changes."""
    for key in DOWNSTREAM_KEYS:
        st.session_state.pop(key, None)

    # Clear dynamically generated artwork widget state.
    for key in list(st.session_state.keys()):
        if key.startswith("artwork_select_"):
            st.session_state.pop(key, None)

        if key.startswith("artwork_qty_"):
            st.session_state.pop(key, None)


class StepCampaign:

    @staticmethod
    def render():

        db = get_session()

        try:

            campaigns = CampaignRepository.get_all(db)

            st.markdown("### Step 1 : Select Campaign")

            if not campaigns:

                st.warning("No Campaigns available.")
                return

            options = {
                f"{c.campaign_name} ({c.campaign_code})": c.id
                for c in campaigns
            }

            option_names = list(options.keys())

            current_campaign = st.session_state.get(
                "selected_campaign"
            )

            default_index = 0

            if current_campaign is not None:

                for index, campaign_id in enumerate(
                    options.values()
                ):
                    if campaign_id == current_campaign:
                        default_index = index
                        break

            selected = st.selectbox(
                "Campaign",
                option_names,
                index=default_index,
            )

            selected_campaign_id = options[selected]

            # Show campaign details before proceeding.
            campaign = next(
                (
                    campaign
                    for campaign in campaigns
                    if campaign.id == selected_campaign_id
                ),
                None,
            )

            if campaign is not None:

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.caption("Client")
                    st.write(campaign.client_name or "-")

                with col2:
                    st.caption("Brand")
                    st.write(campaign.brand_name or "-")

                with col3:
                    st.caption("Status")
                    st.write(
                        getattr(campaign.status, "value", campaign.status)
                        or "-"
                    )

            if st.button(
                "Next ➜",
                type="primary",
                use_container_width=True,
            ):

                if selected_campaign_id is None:

                    st.error("Please select a campaign.")

                else:

                    previous_campaign = st.session_state.get(
                        "selected_campaign"
                    )

                    # If campaign changed, everything below campaign
                    # selection becomes invalid.
                    if previous_campaign != selected_campaign_id:
                        _clear_downstream_state()

                    # Store only the database ID.
                    st.session_state.selected_campaign = (
                        selected_campaign_id
                    )

                    st.session_state.wizard_step = 2

                    st.rerun()

        finally:

            db.close()