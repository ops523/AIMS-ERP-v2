import streamlit as st

from components.wizard.step_campaign import StepCampaign
from components.wizard.step_version import StepVersion


class ProductionBatchWizard:

    @staticmethod
    def render():

        st.subheader("Create Production Batch")

        if "wizard_step" not in st.session_state:
            st.session_state.wizard_step = 1

        if st.session_state.wizard_step == 1:
            StepCampaign.render()

        elif st.session_state.wizard_step == 2:
            StepVersion.render()

        else:
            st.success("More steps coming in next sprint.")
