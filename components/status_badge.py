import streamlit as st


class StatusBadge:

    @staticmethod
    def show(active):

        if active:

            st.success("Active")

        else:

            st.error("Inactive")
