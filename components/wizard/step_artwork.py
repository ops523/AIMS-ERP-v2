from __future__ import annotations

import streamlit as st

from database import get_session

from models.campaign_artwork import CampaignArtwork

from repositories.campaign_artwork_repository import (
    CampaignArtworkRepository,
)


class StepArtwork:

    @staticmethod
    def render():

        version_id = st.session_state.get(
            "selected_version"
        )

        if version_id is None:

            st.error(
                "Campaign Version is not selected. "
                "Please select a campaign version first."
            )

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 2
                st.rerun()

            return

        db = get_session()

        try:

            st.subheader(
                "Step 3 : Select Artworks"
            )

            st.caption(
                "Select the artwork(s) required for this production "
                "batch and enter the number of walls to print."
            )

            artworks = (
                CampaignArtworkRepository.get_by_version(
                    db,
                    version_id,
                )
            )

            if not artworks:

                st.warning(
                    "No artworks have been created for this "
                    "Campaign Version yet."
                )

                st.info(
                    "Create at least one artwork before creating "
                    "a production batch."
                )

            else:

                # --------------------------------------------------
                # Existing selection
                # --------------------------------------------------

                existing_quantities = (
                    st.session_state.get(
                        "artwork_quantities",
                        {},
                    )
                )

                # Make sure the value is always a dictionary.
                if not isinstance(
                    existing_quantities,
                    dict,
                ):
                    existing_quantities = {}

                st.markdown(
                    "#### Production Quantity"
                )

                st.caption(
                    "Quantity means number of walls. "
                    "Planned Sq Ft is calculated automatically."
                )

                rows = []

                for artwork in artworks:

                    artwork_id = artwork.id

                    select_key = (
                        f"artwork_select_{artwork_id}"
                    )

                    quantity_key = (
                        f"artwork_qty_{artwork_id}"
                    )

                    was_selected = (
                        artwork_id in existing_quantities
                    )

                    default_quantity = int(
                        existing_quantities.get(
                            artwork_id,
                            1,
                        )
                    )

                    col1, col2, col3, col4 = st.columns(
                        [3, 1.2, 1.5, 1.5]
                    )

                    with col1:

                        selected = st.checkbox(
                            (
                                f"{artwork.artwork_name} "
                                f"({artwork.artwork_code})"
                            ),
                            value=was_selected,
                            key=select_key,
                        )

                        st.caption(
                            f"Artwork Size: "
                            f"{float(artwork.artwork_sqft):,.2f} Sq Ft"
                        )

                    with col2:

                        quantity = st.number_input(
                            "Walls",
                            min_value=1,
                            step=1,
                            value=max(
                                1,
                                default_quantity,
                            ),
                            key=quantity_key,
                            disabled=not selected,
                        )

                    planned_sqft = (
                        float(artwork.artwork_sqft)
                        * int(quantity)
                        if selected
                        else 0.0
                    )

                    with col3:

                        st.metric(
                            "Planned Sq Ft",
                            f"{planned_sqft:,.2f}",
                        )

                    with col4:

                        assigned_walls = (
                            artwork.assigned_walls or 0
                        )

                        st.metric(
                            "Assigned Walls",
                            f"{assigned_walls:,}",
                        )

                    rows.append(
                        {
                            "artwork": artwork,
                            "selected": selected,
                            "quantity": int(quantity),
                            "planned_sqft": planned_sqft,
                        }
                    )

                    st.divider()

                # --------------------------------------------------
                # Current batch summary
                # --------------------------------------------------

                selected_rows = [
                    row
                    for row in rows
                    if row["selected"]
                    and row["quantity"] > 0
                ]

                total_walls = sum(
                    row["quantity"]
                    for row in selected_rows
                )

                total_planned_sqft = sum(
                    row["planned_sqft"]
                    for row in selected_rows
                )

                st.markdown(
                    "### Batch Artwork Summary"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Total Walls",
                        f"{total_walls:,}",
                    )

                with col2:

                    st.metric(
                        "Total Planned Sq Ft",
                        f"{total_planned_sqft:,.2f}",
                    )

            # --------------------------------------------------
            # Create New Artwork
            # --------------------------------------------------

            st.divider()

            st.markdown(
                "#### Create Artwork"
            )

            with st.form(
                "create_campaign_artwork_form"
            ):

                artwork_code = st.text_input(
                    "Artwork Code",
                    placeholder="ART-001",
                )

                artwork_name = st.text_input(
                    "Artwork Name",
                    placeholder="Main Campaign Artwork",
                )

                file_name = st.text_input(
                    "File Name",
                    placeholder="campaign_artwork.pdf",
                )

                col1, col2 = st.columns(2)

                with col1:

                    width_ft = st.number_input(
                        "Width (ft)",
                        min_value=0.01,
                        step=0.5,
                        value=4.0,
                    )

                with col2:

                    height_ft = st.number_input(
                        "Height (ft)",
                        min_value=0.01,
                        step=0.5,
                        value=8.0,
                    )

                artwork_sqft = (
                    float(width_ft)
                    * float(height_ft)
                )

                st.info(
                    f"Artwork Size: "
                    f"**{artwork_sqft:,.2f} Sq Ft**"
                )

                create_artwork = st.form_submit_button(
                    "➕ Create Artwork",
                    type="primary",
                )

            if create_artwork:

                artwork_code_clean = (
                    artwork_code.strip()
                )

                artwork_name_clean = (
                    artwork_name.strip()
                )

                file_name_clean = (
                    file_name.strip()
                )

                if not artwork_code_clean:

                    st.error(
                        "Artwork Code is required."
                    )

                elif not artwork_name_clean:

                    st.error(
                        "Artwork Name is required."
                    )

                elif not file_name_clean:

                    st.error(
                        "File Name is required."
                    )

                elif width_ft <= 0:

                    st.error(
                        "Width must be greater than zero."
                    )

                elif height_ft <= 0:

                    st.error(
                        "Height must be greater than zero."
                    )

                else:

                    existing = (
                        db.query(CampaignArtwork)
                        .filter(
                            CampaignArtwork.artwork_code
                            == artwork_code_clean
                        )
                        .first()
                    )

                    if existing:

                        st.error(
                            (
                                "Artwork Code "
                                f"'{artwork_code_clean}' "
                                "already exists."
                            )
                        )

                    else:

                        try:

                            artwork = CampaignArtwork(

                                campaign_version_id=version_id,

                                artwork_code=(
                                    artwork_code_clean
                                ),

                                artwork_name=(
                                    artwork_name_clean
                                ),

                                file_name=(
                                    file_name_clean
                                ),

                                width_ft=float(
                                    width_ft
                                ),

                                height_ft=float(
                                    height_ft
                                ),

                                artwork_sqft=float(
                                    artwork_sqft
                                ),

                                assigned_walls=0,
                            )

                            db.add(artwork)

                            db.commit()

                            db.refresh(
                                artwork
                            )

                            st.success(
                                (
                                    "Artwork "
                                    f"'{artwork.artwork_name}' "
                                    "created successfully."
                                )
                            )

                            st.rerun()

                        except Exception as exc:

                            db.rollback()

                            st.error(
                                "Unable to create artwork."
                            )

                            st.exception(exc)

            # --------------------------------------------------
            # Navigation
            # --------------------------------------------------

            st.divider()

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "⬅ Back",
                    use_container_width=True,
                ):

                    st.session_state.wizard_step = 2

                    st.rerun()

            with c2:

                if st.button(
                    "Next ➜",
                    type="primary",
                    use_container_width=True,
                ):

                    # Rebuild the selection from the current
                    # widget state. Only primitive IDs/quantities
                    # are placed into session state.
                    selected_artworks = {}
                    total_planned_sqft = 0.0

                    for row in rows:

                        if not row["selected"]:
                            continue

                        quantity = int(
                            row["quantity"]
                        )

                        if quantity <= 0:
                            continue

                        artwork_id = row[
                            "artwork"
                        ].id

                        planned_sqft = float(
                            row["planned_sqft"]
                        )

                        selected_artworks[
                            artwork_id
                        ] = {
                            "artwork_id": artwork_id,
                            "quantity": quantity,
                            "planned_sqft": planned_sqft,
                        }

                        total_planned_sqft += (
                            planned_sqft
                        )

                    if not selected_artworks:

                        st.error(
                            "Select at least one artwork "
                            "and enter a quantity."
                        )

                        return

                    if total_planned_sqft <= 0:

                        st.error(
                            "Total planned Sq Ft must be greater than zero."
                        )

                        return

                    st.session_state.selected_artworks = (
                        selected_artworks
                    )

                    # Separate simple quantity map is useful to
                    # later wizard steps and keeps the state easy
                    # to consume.
                    st.session_state.artwork_quantities = {
                        artwork_id: data["quantity"]
                        for artwork_id, data
                        in selected_artworks.items()
                    }

                    st.session_state.total_planned_sqft = (
                        total_planned_sqft
                    )

                    st.session_state.wizard_step = 4

                    st.rerun()

        finally:

            db.close()