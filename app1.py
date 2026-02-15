import streamlit as st
import requests

# 🔥 IMPORTANT: Replace with your Render backend URL
API_URL = "https://your-backend-name.onrender.com"

st.set_page_config(page_title="Aura Crypt", layout="centered")

st.title("🔐 Aura Crypt Authentication System")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ---------------- REGISTER FUNCTION ----------------
def register_user(username, email, password):
    try:
        response = requests.post(
            f"{API_URL}/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        return response
    except Exception as e:
        return None


# ---------------- LOGIN FUNCTION ----------------
def login_user(email, password):
    try:
        response = requests.post(
            f"{API_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )
        return response
    except Exception as e:
        return None


# ---------------- MAIN UI ----------------
menu = st.sidebar.selectbox("Select Option", ["Login", "Register"])

# ================= REGISTER =================
if menu == "Register":

    st.subheader("Create New Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if username and email and password:
            response = register_user(username, email, password)

            if response is None:
                st.error("❌ Cannot connect to server")
            elif response.status_code == 200:
                st.success("✅ Registered Successfully!")
            else:
                st.error(response.json().get("detail", "Registration Failed"))
        else:
            st.warning("⚠ Please fill all fields")


# ================= LOGIN =================
elif menu == "Login":

    st.subheader("Login to Your Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            response = login_user(email, password)

            if response is None:
                st.error("❌ Cannot connect to server")
            elif response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("✅ Login Successful!")
                st.rerun()
            else:
                st.error(response.json().get("detail", "Login Failed"))
        else:
            st.warning("⚠ Please fill all fields")


# ================= AFTER LOGIN =================
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    
    st.subheader("🎉 Welcome to Aura Crypt!")
    st.write("You are successfully logged in.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()
