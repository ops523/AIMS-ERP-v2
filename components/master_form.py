import streamlit as st


class MasterForm:

    @staticmethod
    def render():

        code = st.text_input(
            "Code",
            disabled=True
        )

        name = st.text_input(
            "Name"
        )

        active = st.checkbox(
            "Active",
            value=True
        )

        return {

            "code": code,

            "name": name,

            "active": active

        }
