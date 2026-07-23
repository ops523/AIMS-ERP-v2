from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode,
    DataReturnMode,
)


class AgGridTable:

    @staticmethod
    def editable(df):

        gb = GridOptionsBuilder.from_dataframe(df)

        gb.configure_default_column(
            editable=True,
            sortable=True,
            filter=True,
            resizable=True,
        )

        gb.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
        )

        return AgGrid(
            df,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            fit_columns_on_grid_load=True,
            height=450,
        )
