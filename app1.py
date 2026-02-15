# ==================================
# 🌌 VARI-CRYPT: EVENT HORIZON
# ==================================

import streamlit as st
import requests
import io
import os
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine
from audio_engine import AudioStego

# ==============================
# 🔗 BACKEND SERVER
# ==============================
SERVER_URL = "https://vari-crypt-app.onrender.com"  # Keep your backend URL

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
st.set_page_config(page_title="Vari-Crypt: Event Horizon", page_icon="🌌", layout="wide")
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

        # ---------------- LOGIN ----------------
        with tab1:
            l_id = st.text_input("PILOT ID", key="login_id")
            l_pw = st.text_input("ACCESS CODE", type="password", key="login_pw")

            if st.button("INITIATE DOCKING"):
                if not l_id or not l_pw:
                    st.warning("Please enter credentials.")
                else:
                    try:
                        res = requests.post(
                            f"{SERVER_URL}/login",
                            json={"identifier": l_id, "password": l_pw},
                            timeout=10
                        )

                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.user_email = l_id
                            st.success("ACCESS GRANTED")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "ACCESS DENIED"))

                    except Exception as e:
                        st.error(f"SERVER OFFLINE: {e}")

        # ---------------- REGISTER ----------------
        with tab2:
            r_id = st.text_input("NEW PILOT ID", key="reg_id")
            r_pw = st.text_input("SET ACCESS CODE", type="password", key="reg_pw")

            if st.button("CREATE IDENTITY"):
                if not r_id or not r_pw:
                    st.warning("Please enter details.")
                else:
                    try:
                        res = requests.post(
                            f"{SERVER_URL}/register",
                            json={"identifier": r_id, "password": r_pw},
                            timeout=10
                        )

                        if res.status_code == 200:
                            st.success("IDENTITY ESTABLISHED. Please login.")
                        else:
                            st.error(res.json().get("detail", "REGISTRATION FAILED"))

                    except Exception as e:
                        st.error(f"SERVER ERROR: {e}")

# ==========================================
# 🌌 MAIN APPLICATION
# ==========================================
else:

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown(f"### 👨‍🚀 PILOT: `{st.session_state.user_email}`")
        operation = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

        if st.button("LOGOUT / EJECT"):
            st.session_state.logged_in = False
            st.rerun()

    # ==========================================
    # 📡 ENCODE SIGNAL
    # ==========================================
    if operation == "📡 ENCODE SIGNAL":

        st.subheader("// GENERATE SECURE TRANSMISSION")

        msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)")
        pwd = st.text_input("ENCRYPTION KEY", type="password")

        mode = st.selectbox(
            "PROTOCOL",
            [
                "WILDLIFE AUTO-GEN (IMAGE)",
                "EMOJI MAPPING",
                "MANUAL IMAGE UPLOAD",
                "AUDIO ENCRYPTION",
            ],
        )

        uploaded_file = None
        if "MANUAL" in mode:
            uploaded_file = st.file_uploader("UPLOAD IMAGE", type=["png", "jpg"])
        elif "AUDIO" in mode:
            uploaded_file = st.file_uploader("UPLOAD AUDIO", type=["wav", "mp3"])

        if st.button("SEND SIGNAL"):
            if not msg or not pwd:
                st.warning("Message and key required.")
            else:
                try:
                    # Encrypt
                    s, n, t, c = st.session_state.crypto.encrypt_data(msg, pwd)
                    full_hex = (s + n + t + c).hex()

                    # Mode handling
                    if "EMOJI" in mode:
                        output = st.session_state.mapper.map_ciphertext(
                            bytes.fromhex(full_hex), pwd
                        )
                        st.code(output)
                        sync_data = output

                    elif "WILDLIFE" in mode:
                        data = st.session_state.stego.hide_data(
                            None, full_hex, use_wildlife=True
                        )
                        st.image(data)
                        st.download_button("SAVE IMAGE", data, "wildlife.png")
                        sync_data = full_hex

                    elif "MANUAL" in mode and uploaded_file:
                        data = st.session_state.stego.hide_data(
                            uploaded_file, full_hex
                        )
                        st.image(data)
                        st.download_button("SAVE IMAGE", data, "mission.png")
                        sync_data = full_hex

                    elif "AUDIO" in mode and uploaded_file:
                        data = st.session_state.audio_stego.hide_data(
                            uploaded_file, full_hex
                        )
                        st.audio(data)
                        st.download_button("SAVE AUDIO", data, "signal.wav")
                        sync_data = full_hex
                    else:
                        st.error("Upload required for selected mode.")
                        st.stop()

                    # Send to server
                    res = requests.post(
                        f"{SERVER_URL}/send",
                        json={"encrypted_payload": {"visual_data": sync_data}},
                        timeout=10,
                    )

                    if res.status_code == 200:
                        st.info(f"MISSION ID: {res.json().get('msg_id')}")
                        st.success("TRANSMITTED SUCCESSFULLY")
                    else:
                        st.error("SERVER STORAGE FAILED")

                except Exception as e:
                    st.error(f"ENCRYPTION FAILED: {e}")

    # ==========================================
    # 📥 DECODE SIGNAL
    # ==========================================
    else:

        st.subheader("// RECOVER SIGNAL")

        method = st.radio(
            "SOURCE TYPE",
            [
                "CLOUD MISSION ID",
                "MANUAL EMOJI SYMBOLS",
                "IMAGE FILE",
                "AUDIO FILE",
            ],
        )

        decrypt_key = st.text_input("DECRYPT KEY", type="password")

        extracted_hex = None

        try:

            if method == "CLOUD MISSION ID":
                mission_id = st.text_input("MISSION ID")

                if st.button("PULL DATA") and mission_id:
                    res = requests.get(
                        f"{SERVER_URL}/receive/{mission_id}", timeout=10
                    )

                    if res.status_code == 200:
                        raw_data = res.json()["visual_data"]

                        if any(c in raw_data for c in "ΑΒΓΔ"):
                            extracted_hex = (
                                st.session_state.mapper.unmap_ciphertext(
                                    raw_data, decrypt_key
                                ).hex()
                            )
                        else:
                            extracted_hex = raw_data
                    else:
                        st.error(res.json().get("detail", "NOT FOUND"))

            elif method == "MANUAL EMOJI SYMBOLS":
                emoji_input = st.text_area("PASTE SYMBOLS")

                if st.button("TRANSLATE"):
                    extracted_hex = (
                        st.session_state.mapper.unmap_ciphertext(
                            emoji_input, decrypt_key
                        ).hex()
                    )

            elif method == "IMAGE FILE":
                uploaded = st.file_uploader("UPLOAD IMAGE", type=["png", "jpg"])

                if st.button("SCAN") and uploaded:
                    extracted_hex = st.session_state.stego.reveal_data(uploaded)

            elif method == "AUDIO FILE":
                uploaded = st.file_uploader("UPLOAD AUDIO", type=["wav", "mp3"])

                if st.button("ANALYZE") and uploaded:
                    extracted_hex = st.session_state.audio_stego.reveal_data(uploaded)

            # Final Decryption
            if extracted_hex and decrypt_key:
                try:
                    b = bytes.fromhex(extracted_hex)
                    decrypted = st.session_state.crypto.decrypt_data(
                        b[:16], b[16:32], b[32:48], b[48:], decrypt_key
                    )
                    st.success(f"🔓 RECOVERED: {decrypted}")
                    st.balloons()
                except:
                    st.error("DECRYPTION FAILED")

        except Exception as e:
            st.error(f"PROCESS FAILED: {e}")
