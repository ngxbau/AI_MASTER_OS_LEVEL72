import streamlit as st

st.title("💼 BUSINESS EMPIRE")

business = st.text_input("Tên dự án")

offer = st.text_area("Sản phẩm")

if st.button("Build Business"):

    result = f"""
BUSINESS SYSTEM

Project:
{business}

Offer:
{offer}

Business model ready.
"""

    st.code(result)