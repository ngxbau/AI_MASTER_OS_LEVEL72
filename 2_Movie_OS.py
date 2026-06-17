import streamlit as st

st.title("🎞 MOVIE OS")

story = st.text_area("Câu chuyện")

character = st.text_input("Nhân vật")

if st.button("Tạo Story Engine"):

    result = f"""
MOVIE ENGINE

Story:
{story}

Character:
{character}

Generated cinematic universe ready.
"""

    st.code(result)