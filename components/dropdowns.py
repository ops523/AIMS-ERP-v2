import streamlit as st


def supplier_dropdown(data):

    if not data:

        st.warning(

            "No Suppliers Found"

        )

        return None

    return st.selectbox(

        "Supplier",

        data,

        format_func=lambda x:

        x.supplier_name

    )


def manufacturer_dropdown(data):

    return st.selectbox(

        "Manufacturer",

        data,

        format_func=lambda x:

        x.manufacturer_name

    )


def warehouse_dropdown(data):

    return st.selectbox(

        "Warehouse",

        data,

        format_func=lambda x:

        x.warehouse_name

    )


def product_dropdown(data):

    return st.selectbox(

        "Media Product",

        data,

        format_func=lambda x:

        x.product_name

    )
