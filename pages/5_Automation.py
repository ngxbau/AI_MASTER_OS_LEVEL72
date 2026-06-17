import streamlit as st

st.title("⚙️ AUTOMATION")

task = st.text_area("Task")

if st.button("Run Automation"):

    result = f"""
AUTOMATION ENGINE

Task:
{task}

Automation workflow generated.
"""

    st.code(result)