import streamlit as st
import requests

# 🔥 PUT YOUR REAL BACKEND URL HERE
API_URL = "https://your-backend-name.onrender.com"

st.set_page_config(page_title="Aura Crypt", layout="centered")
st.title("🔐 Aura Crypt Authentication")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def safe_request(url, payload):
    try:
        response = requests.post(url, json=payload)

        # Try parsing JSON safely
        try:
            data = response.json()
        except:
            return response.status_code, {"detail": "Server returned invalid response"}

        return response.status_code, data

    except requests.exceptions.RequestException:
        return None, {"detail": "Cannot connect to backend server"}


menu = st.sidebar.selectbox("Select Option", ["Login", "Register"])

# ================= REGISTER =================
if menu == "Register":

    st.subheader("Create Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        if not username or not email or not password:
            st.warning("Please fill all fields")
        else:
            status, data = safe_request(
                f"{API_URL}/register",
                {
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            if status == 200:
                st.success("Registered Successfully ✅")
            else:
                st.error(data.get("detail", "Registration Failed"))


# ================= LOGIN =================
if menu == "Login":

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if not email or not password:
            st.warning("Please fill all fields")
        else:
            status, data = safe_request(
                f"{API_URL}/login",
                {
                    "email": email,
                    "password": password
                }
            )

            if status == 200:
                st.session_state.logged_in = True
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error(data.get("detail", "Login Failed"))


if st.session_state.logged_in:
    st.success("🎉 You are logged in!")
