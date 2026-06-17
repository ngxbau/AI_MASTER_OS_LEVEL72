import streamlit as st
import pandas as pd
import os
from datetime import datetime

USER_PATH = "data/users.csv"

def init_user_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(USER_PATH):
        df = pd.DataFrame({
            "username": ["admin"],
            "password": ["baudeptrai"],
            "role": ["admin"],
            "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        df.to_csv(USER_PATH, index=False)

def load_users():
    init_user_db()
    return pd.read_csv(USER_PATH)

def login_system():
    init_user_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "role" not in st.session_state:
        st.session_state.role = ""

    if not st.session_state.logged_in:
        st.title("🔐 AI MASTER LOGIN SYSTEM — LEVEL 52")

        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("🚀 Đăng nhập"):
            users = load_users()

            match = users[
                (users["username"].astype(str) == username) &
                (users["password"].astype(str) == password)
            ]

            if len(match) > 0:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = match.iloc[0]["role"]

                st.success("✅ Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tài khoản hoặc mật khẩu")

        st.stop()

    return st.session_state.logged_in

def logout_button():
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 {st.session_state.username}")
    st.sidebar.info(f"🔑 Role: {st.session_state.role}")

    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "admin"
        st.rerun()