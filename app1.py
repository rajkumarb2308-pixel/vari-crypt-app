import streamlit as st
import requests

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = "https://vari-crypt-app.onrender.com"  # change if needed

st.set_page_config(page_title="Aura Crypt", layout="centered")

st.title("🔐 Aura Crypt Authentication")

option = st.selectbox("Select Option", ["Register", "Login"])

# -----------------------------
# REGISTER
# -----------------------------
if option == "Register":
    st.subheader("Create Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not username or not email or not password:
            st.error("All fields are required")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/register",
                    json={
                        "username": username,
                        "email": email,
                        "password": password
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(data["message"])
                else:
                    error_data = response.json()
                    st.error(error_data.get("detail", "Registration failed"))

            except requests.exceptions.RequestException:
                st.error("Server not reachable")

# -----------------------------
# LOGIN
# -----------------------------
if option == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.error("All fields are required")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/login",
                    json={
                        "email": email,
                        "password": password
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(data["message"])
                else:
                    error_data = response.json()
                    st.error(error_data.get("detail", "Login failed"))

            except requests.exceptions.RequestException:
                st.error("Server not reachable")
