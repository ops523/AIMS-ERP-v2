import streamlit as st


def load_theme():

    try:

        with open("assets/styles.css") as f:

            st.markdown(

                f"<style>{f.read()}</style>",

                unsafe_allow_html=True,

            )

    except FileNotFoundError:

        pass
