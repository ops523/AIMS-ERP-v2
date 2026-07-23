import pandas as pd
import streamlit as st


class MasterTable:

    @staticmethod
    def show(records):

        if not records:

            st.info("No records found.")

            return

        data = []

        for r in records:

            data.append({

                "Code": r.code,

                "Name": r.name,

                "Status": "Active" if r.active else "Inactive"

            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
