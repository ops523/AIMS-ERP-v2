import streamlit as st


class StatCard:

    @staticmethod
    def render(
        title,
        value,
        delta=None,
    ):

        st.metric(
            label=title,
            value=value,
            delta=delta,
        )
