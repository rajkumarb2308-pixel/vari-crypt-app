# ==================================
# 🌌 VARI-CRYPT: EVENT HORIZON
# ==================================

import streamlit as st
import requests
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine
from audio_engine import AudioStego

# ==============================
# 🔗 BACKEND SERVER
# ==============================
SERVER_URL = "https://vari-crypt-app.onrender.com"
REQUEST_TIMEOUT = 60  # Increased for Render cold start

# ==============================
# 🚀 ENGINE INITIALIZATION
# ==============================
if "engines_loaded" not in st.session_state:
    st.session_state.crypto = CryptoEngine()
    st.session_state.mapper = MappingEngine()
    st.session_state.stego = StegoEngine()
    st.session_state.audio_stego = AudioStego()
    st.session_state.engines_loaded = True

# ==============================
# 🎨 PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Vari-Crypt: Event Horizon",
    page_icon="🌌",
    layout="wide"
)
st.title("VARI-CRYPT: EVENT HORIZON")

# ==============================
# 🔐 SESSION STATE
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ==========================================
# 🔐 LOGIN / REGISTER
# ==========================================
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["🚀 LOGIN", "📝 REGISTER"])

        # LOGIN
        with tab1:
            l_id = st.text_input("PILOT ID")
            l_pw = st.text_input("ACCESS CODE", type="password")

            if st.button("INITIATE DOCKING"):
                if not l_id or not l_pw:
                    st.warning("Please enter credentials.")
                else:
                    try:
                        res = requests.post(
                            f"{SERVER_URL}/login",
                            json={"identifier": l_id, "password": l_pw},
                            timeout=REQUEST_TIMEOUT
                        )

                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.user_email = l_id
                            st.success("ACCESS GRANTED")
                            st.rerun()
                        else:
                            st.error(f"{res.status_code} - {res.text}")

                    except requests.exceptions.Timeout:
                        st.error("Server waking up... please wait and try again.")
                    except Exception as e:
                        st.error(f"Server error: {e}")

        # REGISTER
        with tab2:
            r_id = st.text_input("NEW PILOT ID")
            r_pw = st.text_input("SET ACCESS CODE", type="password")

            if st.button("CREATE IDENTITY"):
                if not r_id or not r_pw:
                    st.warning("Please enter details.")
                else:
                    try:
                        res = requests.post(
                            f"{SERVER_URL}/register",
                            json={"identifier": r_id, "password": r_pw},
                            timeout=REQUEST_TIMEOUT
                        )

                        if res.status_code == 200:
                            st.success("IDENTITY ESTABLISHED. Please login.")
                        else:
                            st.error(f"{res.status_code} - {res.text}")

                    except requests.exceptions.Timeout:
                        st.error("Server waking up... please wait and try again.")
                    except Exception as e:
                        st.error(f"Server error: {e}")


# ==========================================
# 🌌 MAIN APPLICATION
# ==========================================
else:

    with st.sidebar:
        st.markdown(f"### 👨‍🚀 PILOT: `{st.session_state.user_email}`")
        operation = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

        if st.button("LOGOUT / EJECT"):
            st.session_state.logged_in = False
            st.rerun()

    # ==========================================
    # 📡 ENCODE
    # ==========================================
    if operation == "📡 ENCODE SIGNAL":

        msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)")
        pwd = st.text_input("ENCRYPTION KEY", type="password")

        if st.button("SEND SIGNAL"):
            if not msg or not pwd:
                st.warning("Message and key required.")
            else:
                try:
                    s, n, t, c = st.session_state.crypto.encrypt_data(msg, pwd)
                    full_hex = (s + n + t + c).hex()

                    res = requests.post(
                        f"{SERVER_URL}/send",
                        json={"encrypted_payload": {"visual_data": full_hex}},
                        timeout=REQUEST_TIMEOUT
                    )

                    if res.status_code == 200:
                        st.success(f"MISSION ID: {res.json()['msg_id']}")
                    else:
                        st.error(f"{res.status_code} - {res.text}")

                except Exception as e:
                    st.error(f"Encryption failed: {e}")

    # ==========================================
    # 📥 DECODE
    # ==========================================
    else:

        mission_id = st.text_input("MISSION ID")
        decrypt_key = st.text_input("DECRYPT KEY", type="password")

        if st.button("PULL DATA") and mission_id:
            try:
                res = requests.get(
                    f"{SERVER_URL}/receive/{mission_id}",
                    timeout=REQUEST_TIMEOUT
                )

                if res.status_code == 200:
                    extracted_hex = res.json()["visual_data"]
                    b = bytes.fromhex(extracted_hex)

                    decrypted = st.session_state.crypto.decrypt_data(
                        b[:16], b[16:32], b[32:48], b[48:], decrypt_key
                    )

                    st.success(f"🔓 RECOVERED: {decrypted}")
                else:
                    st.error(f"{res.status_code} - {res.text}")

            except requests.exceptions.Timeout:
                st.error("Server waking up... try again.")
            except Exception as e:
                st.error(f"Error: {e}")
