import streamlit as st

from core.startup import startup

startup()

st.title("🖨️ Production Batch Wizard")

# ------------------------------------------
# Wizard State
# ------------------------------------------

if "production_step" not in st.session_state:
    st.session_state.production_step = 1

if "selected_campaign" not in st.session_state:
    st.session_state.selected_campaign = None

if "selected_version" not in st.session_state:
    st.session_state.selected_version = None

if "selected_printer" not in st.session_state:
    st.session_state.selected_printer = None

if "selected_shift" not in st.session_state:
    st.session_state.selected_shift = "DAY"

if "selected_artworks" not in st.session_state:
    st.session_state.selected_artworks = []

if "selected_rolls" not in st.session_state:
    st.session_state.selected_rolls = []

st.divider()

steps = [
    "Campaign",
    "Printer",
    "Artworks",
    "Media Rolls",
    "Review",
    "Generate",
]

cols = st.columns(len(steps))

for i, step in enumerate(steps):

    if st.session_state.production_step == i + 1:
        cols[i].success(f"{i+1}. {step}")
    else:
        cols[i].info(f"{i+1}. {step}")

st.divider()

if st.session_state.production_step == 1:
    from components.production_step_campaign import render
    render()

elif st.session_state.production_step == 2:
    from components.production_step_printer import render
    render()

elif st.session_state.production_step == 3:
    from components.production_step_artwork import render
    render()

elif st.session_state.production_step == 4:
    from components.production_step_roll import render
    render()

elif st.session_state.production_step == 5:
    from components.production_step_review import render
    render()

elif st.session_state.production_step == 6:
    from components.production_step_generate import render
    render()
