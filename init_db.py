from database import Base
from database import engine
from database import SessionLocal

import models

from services.seed_service import seed_database


def initialize_database():

    from sqlalchemy import inspect
    import streamlit as st

    inspector = inspect(engine)

    st.sidebar.write("Tables before create_all()")
    st.sidebar.write(inspector.get_table_names())

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    st.sidebar.write("Tables after create_all()")
    st.sidebar.write(inspector.get_table_names())
    
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()
