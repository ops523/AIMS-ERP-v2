import streamlit as st

from components.wizard.step_campaign import StepCampaign
from components.wizard.step_version import StepVersion
from components.wizard.step_artwork import StepArtwork
from components.wizard.step_printer import StepPrinter
from components.wizard.step_rolls import StepRolls
from components.wizard.step_review import StepReview


class ProductionBatchWizard:

    @staticmethod
    def render():

        if "wizard_step" not in st.session_state:
            st.session_state.wizard_step = 1

        st.progress(st.session_state.wizard_step / 6)

        st.caption(
            f"Step {st.session_state.wizard_step} of 6"
        )

        if st.session_state.wizard_step == 1:
            StepCampaign.render()

        elif st.session_state.wizard_step == 2:
            StepVersion.render()

        elif st.session_state.wizard_step == 3:
            StepArtwork.render()

        elif st.session_state.wizard_step == 4:
            StepPrinter.render()

        elif st.session_state.wizard_step == 5:
            StepRolls.render()

        elif st.session_state.wizard_step == 6:
            StepReview.render()
