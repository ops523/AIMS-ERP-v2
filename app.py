import streamlit as st

from init_db import initialize_database

initialize_database()

st.set_page_config(

    page_title="AIMS ERP",

    layout="wide"

)

st.title("AIMS ERP")

st.success("Foundation Loaded Successfully")

st.write("Sprint 1 Version 2")

if page == "Campaign Import Wizard":
    from pages.campaign_wizard import *
