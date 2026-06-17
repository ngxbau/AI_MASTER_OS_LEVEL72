import streamlit as st
from login import login_system, logout_button

st.set_page_config(
    page_title="AI MASTER OS",
    page_icon="🚀",
    layout="wide"
)
if login_system():
    logout_button()
else:
    st.stop()

st.markdown("""
# 🚀 AI MASTER OS — LEVEL 72

### Hệ điều hành AI đa trang đã public thành công

✅ Video Studio
✅ Movie OS
✅ Brand Empire
✅ Business Empire
✅ Automation
✅ Dashboard
✅ Memory System
✅ Prompt History
✅ Upload ảnh tham chiếu Veo 3
""")