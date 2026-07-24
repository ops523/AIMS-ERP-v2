import streamlit as st


class PageHeader:

    @staticmethod
    def render(
        title: str,
        subtitle: str = "",
        icon: str = "📄",
    ):

        col1, col2 = st.columns([1, 8])

        with col1:
            st.markdown(
                f"<h1 style='font-size:48px'>{icon}</h1>",
                unsafe_allow_html=True,
            )

        with col2:

            st.title(title)

            if subtitle:
                st.caption(subtitle)

        st.divider()
