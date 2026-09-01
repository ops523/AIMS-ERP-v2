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

        db = get_session()

        try:

            version_id = st.session_state.get(
                "selected_version"
            )

            if version_id is None:

                st.error(
                    "Campaign Version is not selected."
                )

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 2

                    st.rerun()

                return

            st.subheader(
                "Step 3 : Select / Create Artworks"
            )

            # --------------------------------------------------
            # Existing Artworks
            # --------------------------------------------------

            artworks = (
                CampaignArtworkRepository.get_by_version(
                    db,
                    version_id,
                )
            )

            if artworks:

                st.markdown(
                    "#### Existing Artworks"
                )

                selected = []

                for artwork in artworks:

                    label = (
                        f"{artwork.artwork_name} "
                        f"({artwork.artwork_sqft:.2f} Sq Ft)"
                    )

                    if st.checkbox(
                        label,
                        key=f"artwork_select_{artwork.id}",
                    ):

                        selected.append(
                            artwork.id
                        )

                st.session_state[
                    "selected_artworks"
                ] = selected

            else:

                st.info(
                    "No artworks have been created "
                    "for this Campaign Version yet."
                )

            st.divider()

            # --------------------------------------------------
            # Create New Artwork
            # --------------------------------------------------

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
                    width_ft * height_ft
                )

                st.info(
                    f"Artwork Size: "
                    f"**{artwork_sqft:.2f} Sq Ft**"
                )

                create_artwork = st.form_submit_button(
                    "➕ Create Artwork",
                    type="primary",
                )

            if create_artwork:

                # ------------------------------------------
                # Validation
                # ------------------------------------------

                if not artwork_code.strip():

                    st.error(
                        "Artwork Code is required."
                    )

                elif not artwork_name.strip():

                    st.error(
                        "Artwork Name is required."
                    )

                elif not file_name.strip():

                    st.error(
                        "File Name is required."
                    )

                else:

                    existing = (
                        db.query(CampaignArtwork)
                        .filter(
                            CampaignArtwork.artwork_code
                            == artwork_code.strip()
                        )
                        .first()
                    )

                    if existing:

                        st.error(
                            (
                                "Artwork Code "
                                f"'{artwork_code.strip()}' "
                                "already exists."
                            )
                        )

                    else:

                        try:

                            artwork = CampaignArtwork(

                                campaign_version_id=(
                                    version_id
                                ),

                                artwork_code=(
                                    artwork_code.strip()
                                ),

                                artwork_name=(
                                    artwork_name.strip()
                                ),

                                file_name=(
                                    file_name.strip()
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

            st.divider()

            # --------------------------------------------------
            # Navigation
            # --------------------------------------------------

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

                    selected_artworks = (
                        st.session_state.get(
                            "selected_artworks",
                            [],
                        )
                    )

                    if not selected_artworks:

                        st.error(
                            "Select at least one artwork."
                        )

                    else:

                        st.session_state[
                            "selected_artworks"
                        ] = selected_artworks

                        st.session_state[
                            "wizard_step"
                        ] = 4

                        st.rerun()

        finally:

            db.close()