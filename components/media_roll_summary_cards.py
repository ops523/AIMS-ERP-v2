import streamlit as st

from services.media_roll_service import MediaRollService


class MediaRollSummaryCards:

    @staticmethod
    def render(db):

        summary = MediaRollService.dashboard(db)

        st.subheader("Media Roll Inventory")

        # -------------------------------------------------
        # ROLL COUNTS
        # -------------------------------------------------

        cols = st.columns(5)

        cards = [
            ("Total Rolls", summary.get("total", 0)),
            ("Available", summary.get("available", 0)),
            ("Reserved", summary.get("reserved", 0)),
            ("Allocated", summary.get("allocated", 0)),
            ("Printing", summary.get("printing", 0)),
        ]

        for column, (label, value) in zip(
            cols,
            cards,
        ):

            with column:

                st.metric(
                    label=label,
                    value=value,
                )

        cols = st.columns(5)

        cards = [
            ("Printed", summary.get("printed", 0)),
            (
                "Partially Used",
                summary.get("partially_used", 0),
            ),
            ("Consumed", summary.get("consumed", 0)),
            ("Returned", summary.get("returned", 0)),
            ("Damaged", summary.get("damaged", 0)),
        ]

        for column, (label, value) in zip(
            cols,
            cards,
        ):

            with column:

                st.metric(
                    label=label,
                    value=value,
                )

        lost = summary.get("lost", 0)

        if lost:

            st.warning(
                f"{lost} media roll(s) currently marked LOST."
            )
