import streamlit as st

st.title("Autonomous Database Investigation Agent")

# Initialize a counter in session_state, but only the very first time
if "click_count" not in st.session_state:
    st.session_state.click_count = 0

if st.button("Click me"):
    st.session_state.click_count += 1

st.write("Total clicks so far:", st.session_state.click_count)