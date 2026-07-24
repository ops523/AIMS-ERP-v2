import streamlit as st


class Statistics:

    @staticmethod
    def cards(stats):

        cols = st.columns(len(stats))

        for col, item in zip(cols, stats):

            with col:

                st.metric(

                    item["title"],

                    item["value"],

                    item.get("delta"),

                )
