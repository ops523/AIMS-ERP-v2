import streamlit as st
from sqlalchemy.orm import Session

from repositories.media_roll_repository import MediaRollRepository


class MediaRollSummaryCards:

    @staticmethod
    def render(db: Session):

        summary = MediaRollRepository.summary(db)

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                label="Total Rolls",
                value=summary["total"],
            )

        with col2:

            st.metric(
                label="Available",
                value=summary["available"],
            )

        with col3:

            st.metric(
                label="Allocated",
                value=summary["allocated"],
            )

        with col4:

            st.metric(
                label="Consumed",
                value=summary["consumed"],
            )
