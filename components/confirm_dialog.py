import streamlit as st


class ConfirmDialog:

    @staticmethod
    def confirm(message):

        return st.checkbox(message)
