import streamlit as st


class Breadcrumbs:

    @staticmethod
    def render(*items):

        st.caption("  >  ".join(items))
