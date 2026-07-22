import streamlit as st

from database import get_session

from repositories.supplier_repository import SupplierRepository

from repositories.manufacturer_repository import ManufacturerRepository

from repositories.warehouse_repository import WarehouseRepository

from repositories.media_product_repository import MediaProductRepository

from components.dropdowns import *

db = get_session()

suppliers = SupplierRepository.get_all(db)

manufacturers = ManufacturerRepository.get_all(db)

warehouses = WarehouseRepository.get_all(db)

products = MediaProductRepository.get_all(db)

st.title("Receive Media Rolls")

c1, c2 = st.columns(2)

with c1:

    supplier = supplier_dropdown(suppliers)

    manufacturer = manufacturer_dropdown(manufacturers)

    warehouse = warehouse_dropdown(warehouses)

with c2:

    product = product_dropdown(products)

    po = st.text_input("Purchase Order")

    invoice = st.text_input("Invoice Number")

invoice_date = st.date_input(

    "Invoice Date"

)

st.divider()

rolls = st.number_input(

    "Number of Rolls",

    1,

    100,

    1

)

ordered_length = st.number_input(

    "Ordered Length (Meters)",

    value=50.0

)

width = st.selectbox(

    "Width (Feet)",

    [4,5]

)

if st.button(

    "Create Roll Entry"

):

    st.session_state.roll_count = rolls
