import streamlit as st


class MasterToolbar:

    @staticmethod
    def render():

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            add = st.button(
                "➕ Add New",
                use_container_width=True,
            )

        with c2:
            refresh = st.button(
                "🔄 Refresh",
                use_container_width=True,
            )

        with c3:
            export = st.button(
                "📥 Export",
                use_container_width=True,
            )

        with c4:
            search = st.text_input(
                "Search",
                label_visibility="collapsed",
                placeholder="Search...",
            )

        return {

            "add": add,

            "refresh": refresh,

            "export": export,

            "search": search,

        }
