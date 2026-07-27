import streamlit as st


class StepPrinter:

    @staticmethod
    def render():

        st.subheader("Step 4 : Select Printer")

        st.info(
            "Printer allocation will be implemented next."
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button("⬅ Back"):

                st.session_state.wizard_step = 3

                st.rerun()

        with c2:

            if st.button(
                "Next ➜",
                type="primary",
            ):

                st.session_state.wizard_step = 5

                st.rerun()
