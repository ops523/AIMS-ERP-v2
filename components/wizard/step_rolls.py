import streamlit as st


class StepRolls:

    @staticmethod
    def render():

        st.subheader("Step 5 : Allocate Media Rolls")

        st.info(
            "Roll allocation will be implemented next."
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 4

                st.rerun()

        with c2:

            if st.button(
                "Next ➜",
                type="primary",
            ):

                st.session_state.wizard_step = 6

                st.rerun()
