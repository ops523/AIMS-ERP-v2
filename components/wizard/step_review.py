import streamlit as st


class StepReview:

    @staticmethod
    def render():

        st.subheader("Step 6 : Review & Create Batch")

        st.success("Review screen will be implemented next.")

        if st.button("⬅ Back"):

            st.session_state.wizard_step = 5

            st.rerun()
