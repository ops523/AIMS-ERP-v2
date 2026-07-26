import streamlit as st
from sqlalchemy import inspect

import models

from database import Base, engine
from config import DATABASE_URL


def initialize_database():

    Base.metadata.create_all(bind=engine)

    st.sidebar.write("### Database Debug")
    st.sidebar.write(DATABASE_URL)

    st.sidebar.write("Registered Models")
    st.sidebar.write(sorted(Base.metadata.tables.keys()))

    inspector = inspect(engine)

    st.sidebar.write("Database Tables")
    st.sidebar.write(inspector.get_table_names())
