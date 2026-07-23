import streamlit as st


class SearchBox:

    @staticmethod
    def render():

        return st.text_input(

            "🔍 Search",

            placeholder="Search..."

        )
