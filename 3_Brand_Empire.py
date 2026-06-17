import streamlit as st

st.title("🏆 BRAND EMPIRE")

brand = st.text_input("Tên thương hiệu")

mission = st.text_area("Sứ mệnh")

if st.button("Build Brand"):

    result = f"""
BRAND SYSTEM

Brand:
{brand}

Mission:
{mission}

Positioning generated.
"""

    st.code(result)