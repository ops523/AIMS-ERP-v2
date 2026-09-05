from __future__ import annotations

import streamlit as st

from database import get_session

from repositories.campaign_version_repository import (
    CampaignVersionRepository,
)


def _clear_downstream_state() -> None:
    """Clear selections that depend on the selected campaign version."""

    keys = (
        "selected_artworks",
        "artwork_quantities",
        "total_planned_sqft",
        "selected_printer",
        "selected_shift",
        "printer_capacity",
    )

    for key in keys:
        st.session_state.pop(key, None)

    # Clear dynamic artwork widget state.
    for key in list(st.session_state.keys()):

        if key.startswith("artwork_select_"):
            st.session_state.pop(key, None)

        if key.startswith("artwork_qty_"):
            st.session_state.pop(key, None)


class StepVersion:

    @staticmethod
    def render():

        campaign_id = st.session_state.get(
            "selected_campaign"
        )

        if campaign_id is None:

            st.error(
                "Campaign is not selected. Please select a campaign first."
            )

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 1
                st.rerun()

            return

        db = get_session()

        try:

            versions = (
                CampaignVersionRepository.get_by_campaign(
                    db,
                    campaign_id,
                )
            )

            st.markdown("### Step 2 : Campaign Version")

            if not versions:

                st.warning("No versions found for this campaign.")

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 1
                    st.rerun()

                return

            options = {
                (
                    f"{v.version_name} "
                    f"(Walls: {v.total_walls:,} | "
                    f"Sq Ft: {v.total_sqft:,.2f})"
                ): v.id
                for v in versions
            }

            option_names = list(options.keys())

            current_version = st.session_state.get(
                "selected_version"
            )

            default_index = 0

            if current_version is not None:

                for index, version_id in enumerate(
                    options.values()
                ):

                    if version_id == current_version:
                        default_index = index
                        break

            selected = st.selectbox(
                "Campaign Version",
                option_names,
                index=default_index,
            )

            selected_version_id = options[selected]

            version = next(
                (
                    version
                    for version in versions
                    if version.id == selected_version_id
                ),
                None,
            )

            if version is not None:

                st.divider()

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.caption("Version")
                    st.write(version.version_name)

                with col2:
                    st.caption("Locations")
                    st.write(f"{version.total_locations:,}")

                with col3:
                    st.caption("Walls")
                    st.write(f"{version.total_walls:,}")

                with col4:
                    st.caption("Total Sq Ft")
                    st.write(f"{version.total_sqft:,.2f}")

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "⬅ Back",
                    use_container_width=True,
                ):

                    st.session_state.wizard_step = 1
                    st.rerun()

            with c2:

                if st.button(
                    "Next ➜",
                    type="primary",
                    use_container_width=True,
                ):

                    if selected_version_id is None:

                        st.error(
                            "Please select a campaign version."
                        )

                    else:

                        previous_version = st.session_state.get(
                            "selected_version"
                        )

                        # If the version changed, all artwork,
                        # printer and roll selections become invalid.
                        if previous_version != selected_version_id:
                            _clear_downstream_state()

                        # Store only the ID.
                        st.session_state.selected_version = (
                            selected_version_id
                        )

                        st.session_state.wizard_step = 3

                        st.rerun()

        finally:

            db.close()