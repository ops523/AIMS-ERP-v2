import streamlit as st

from database import get_session

from repositories.campaign_artwork_repository import (
    CampaignArtworkRepository,
)


class StepArtwork:

    @staticmethod
    def render():

        db = get_session()

        artworks = (
            CampaignArtworkRepository.get_by_version(
                db,
                st.session_state.selected_version,
            )
        )

        st.subheader("Step 3 : Select Artworks")

        if not artworks:

            st.warning("No artworks available.")

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 2

                st.rerun()

            db.close()

            return

        selected = []

        for artwork in artworks:

            if st.checkbox(
                f"{artwork.artwork_name} ({artwork.artwork_sqft:.0f} Sq Ft)",
                key=f"art_{artwork.id}",
            ):

                selected.append(artwork.id)

        c1, c2 = st.columns(2)

        with c1:

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 2

                st.rerun()

        with c2:

            if st.button(
                "Next ➜",
                type="primary",
            ):

                if not selected:

                    st.error("Select at least one artwork.")

                else:

                    st.session_state.selected_artworks = selected

                    st.session_state.wizard_step = 4

                    st.rerun()

        db.close()
