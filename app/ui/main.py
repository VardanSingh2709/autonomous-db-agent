import streamlit as st
import sys
import os

# Allow this file to import from app/database even though
# Streamlit runs this file directly rather than as part of a package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.connection import run_query

st.title("Autonomous Database Investigation Agent")

st.header("Regions in the database")

regions = run_query("SELECT * FROM regions ORDER BY id")
st.dataframe(regions)

st.header("Look up customers by region")

region_names = [r["name"] for r in regions]
selected_region = st.selectbox("Choose a region", region_names)

customers = run_query(
    "SELECT id, name, email, signup_date, is_returning FROM customers WHERE region_id = (SELECT id FROM regions WHERE name = :region) ORDER BY id",
    {"region": selected_region}
)
st.write(f"Customers in {selected_region}:")
st.dataframe(customers)