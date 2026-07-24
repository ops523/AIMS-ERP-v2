import streamlit as st


class Layout:

    @staticmethod
    def page(title):

        st.title(title)

        st.divider()

    @staticmethod
    def section(title):

        st.subheader(title)
