import streamlit as st
import requests
import io
import os
import time
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine
from audio_engine import AudioStego

# --- ENGINE STARTUP ---
if 'engines_loaded' not in st.session_state:
    st.session_state.crypto = CryptoEngine()
    st.session_state.mapper = MappingEngine()
    st.session_state.stego = StegoEngine()
    st.session_state.audio_stego = AudioStego()
    st.session_state.engines_loaded = True

SERVER_URL = "http://127.0.0.1:8000"

# ==========================================
# 🌌 COSMIC CLIFFS: STATIC GLASS EDITION
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Event Horizon", page_icon="🌌", layout="wide")

st.markdown("""
    <style>
    /* 1. BACKGROUND: MOVING COSMIC CLIFFS */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2011&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        animation: cosmic-drift 60s ease-in-out infinite alternate;
    }

    /* 2. OVERLAY: STARDUST (Subtle) */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px);
        background-size: 350px 350px;
        opacity: 0.4;
        animation: stardust-twinkle 10s linear infinite;
        pointer-events: none;
    }

    /* ANIMATIONS (Background Only) */
    @keyframes cosmic-drift {
        0% { background-position: center; transform: scale(1); }
        100% { background-position: 40% 60%; transform: scale(1.1); }
    }
    @keyframes stardust-twinkle {
        0% { opacity: 0.3; } 50% { opacity: 0.6; } 100% { opacity: 0.3; }
    }

    /* 3. STATIC GLASS UI (NO VIBRATION) */

    /* Buttons: Transparent, Fixed, No Movement on Hover */
    div.stButton > button { 
        width: 100%; 
        background: rgba(0, 0, 0, 0.3); /* Transparent Black */
        color: #00ffff; 
        border: 1px solid rgba(0, 255, 255, 0.3); 
        font-weight: bold;
        letter-spacing: 2px; 
        transition: background 0.2s, border 0.2s; /* Color change only */
        backdrop-filter: blur(2px);
    }
    /* HOVER STATE: Color change only, NO movement/scaling */
    div.stButton > button:hover { 
        background: rgba(0, 255, 255, 0.1); 
        color: #fff; 
        border-color: #fff;
        /* box-shadow removed to prevent "pop" effect */
    }
    div.stButton > button:active {
        transform: none !important; /* Forces button to stay still when clicked */
    }

    /* Text Inputs & Areas: Highly Transparent Glass */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        background-color: rgba(0, 0, 0, 0.35) !important; /* 35% Opacity */
        color: #ffffff !important; 
        border: 1px solid rgba(255, 255, 255, 0.2) !important; 
        border-radius: 4px;
        backdrop-filter: blur(3px);
    }

    /* Input Focus State: static highlight */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00ffff !important;
        box-shadow: none !important;
    }

    /* Headers & Labels */
    h1 { color: #fff !important; text-shadow: 0 0 15px #e100ff; text-align: center; font-family: 'Verdana', sans-serif; }
    h2, h3, label, .stMarkdown p { 
        color: #ffffff !important; 
        text-shadow: 0 0 5px #000; 
    }

    /* Sidebar: Semi-Transparent Glass */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.5) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(5px);
    }

    /* Remove default top padding */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("VARI-CRYPT: EVENT HORIZON")

# ==========================================
# 🔐 IDENTITY GATE
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>AUTHENTICATION REQUIRED</h3>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🚀 LOGIN", "📝 REGISTER"])
        with t1:
            l_id = st.text_input("PILOT ID (GMAIL/PHONE)", key="l_id")
            l_pw = st.text_input("ACCESS CODE", type="password", key="l_pw")
            if st.button("INITIATE DOCKING"):
                try:
                    res = requests.post(f"{SERVER_URL}/login", json={"identifier": l_id, "password": l_pw})
                    if res.status_code == 200:
                        st.session_state.logged_in, st.session_state.user_email = True, l_id
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: UNKNOWN SIGNATURE.")
                except:
                    st.error("CONNECTION FAILURE: SERVER UNREACHABLE.")
        with t2:
            r_id = st.text_input("NEW PILOT ID", key="r_id")
            r_pw = st.text_input("SET ACCESS CODE", type="password", key="r_pw")
            if st.button("CREATE IDENTITY"):
                requests.post(f"{SERVER_URL}/register", json={"identifier": r_id, "password": r_pw})
                st.success("IDENTITY LOGGED. PROCEED TO LOGIN.")

# ==========================================
# 🛰️ MISSION CONTROL
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍🚀 PILOT: `{st.session_state.user_email}`")
        st.markdown("---")
        op = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])
        st.markdown("---")
        if st.button("LOGOUT / EJECT"):
            st.session_state.logged_in = False
            st.rerun()

    # ---------------- ENCODE SECTION ----------------
    if op == "📡 ENCODE SIGNAL":
        st.subheader("// GENERATE SECURE TRANSMISSION")
        col1, col2 = st.columns([2, 1])
        with col1:
            msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)", height=100)
        with col2:
            pwd = st.text_input("ENCRYPTION KEY", type="password")

        mode = st.selectbox("OBFUSCATION PROTOCOL", [
            "AUDIO TRANSMISSION (SONIC)",
            "EMOJI MAPPING (ALIEN SYMBOLS)",
            "IMAGE UPLOAD (VISUAL)",
            "NATURE GEN (SYNTHETIC)"
        ])

        up_file = None
        if "IMAGE" in mode:
            up_file = st.file_uploader("UPLOAD CARRIER IMAGE", type=["png", "jpg"])
        elif "AUDIO" in mode:
            up_file = st.file_uploader("UPLOAD CARRIER AUDIO", type=["wav", "mp3", "m4a", "ogg"])

        if st.button("ENGAGE WARP DRIVE (SEND)"):
            try:
                s, n, t, c = st.session_state.crypto.encrypt_data(msg, pwd)
                f_hex = (s + n + t + c).hex()

                if "EMOJI" in mode:
                    st.code(st.session_state.mapper.map_ciphertext(bytes.fromhex(f_hex), pwd))
                elif "NATURE" in mode:
                    data = st.session_state.stego.hide_data(None, f_hex, auto_generate=True)
                    st.image(data, caption="SYNTHETIC REALITY GENERATED");
                    st.download_button("DOWNLOAD ARTIFACT", data, "mission.png")
                elif "IMAGE" in mode and up_file:
                    data = st.session_state.stego.hide_data(up_file, f_hex)
                    st.image(data, caption="DATA EMBEDDED");
                    st.download_button("DOWNLOAD ARTIFACT", data, "mission.png")
                elif "AUDIO" in mode and up_file:
                    with st.spinner("MODULATING FREQUENCIES..."):
                        data = st.session_state.audio_stego.hide_data(up_file, f_hex)
                        st.audio(data)
                        st.download_button("DOWNLOAD SONIC SIGNAL", data, "signal.wav")

                requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": f_hex}})
                st.success("TRANSMISSION SUCCESSFUL. SIGNAL LOCK ESTABLISHED.")
            except Exception as e:
                st.error(f"MISSION FAILURE: {e}")

    # ---------------- DECODE SECTION ----------------
    else:
        st.subheader("// RECOVER SECURE DATA")

        rec_mode = st.selectbox("SOURCE TYPE", [
            "EXTRACT FROM AUDIO FILE",
            "EXTRACT FROM IMAGE FILE",
            "DECODE EMOJI SYMBOLS",
            "CLOUD DATABASE (ID)"
        ])

        k = st.text_input("DECRYPTION KEY", type="password")
        extracted_hex = None

        if "AUDIO" in rec_mode:
            up_file = st.file_uploader("UPLOAD SONIC SIGNAL", type=["wav", "mp3", "m4a"])
            if st.button("ANALYZE FREQUENCIES") and up_file and k:
                try:
                    with st.spinner("DEMODULATING..."):
                        extracted_hex = st.session_state.audio_stego.reveal_data(up_file)
                except Exception as e:
                    st.error(f"ANALYSIS FAILED: {e}")

        elif "IMAGE" in rec_mode:
            up_file = st.file_uploader("UPLOAD VISUAL ARTIFACT", type=["png", "jpg"])
            if st.button("SCAN PIXELS") and up_file and k:
                try:
                    extracted_hex = st.session_state.stego.reveal_data(up_file)
                except Exception as e:
                    st.error(f"SCAN FAILED: {e}")

        elif "EMOJI" in rec_mode:
            emoji_text = st.text_area("PASTE ALIEN SYMBOLS")
            if st.button("TRANSLATE SYMBOLS") and emoji_text and k:
                try:
                    st.info("Manual Decode Required.")
                except Exception as e:
                    st.error(f"TRANSLATION FAILED: {e}")

        elif "CLOUD" in rec_mode:
            mid = st.text_input("MISSION ID")
            if st.button("RETRIEVE FROM ORBIT") and mid and k:
                res = requests.get(f"{SERVER_URL}/receive/{mid}")
                if res.status_code == 200:
                    extracted_hex = res.json()['visual_data']
                else:
                    st.error("SIGNAL LOST IN VOID.")

        if extracted_hex:
            try:
                b = bytes.fromhex(extracted_hex)
                dec = st.session_state.crypto.decrypt_data(b[:16], b[16:32], b[32:48], b[48:], k)

                if dec:
                    st.success(f"🔓 DECRYPTED PAYLOAD: {dec}")
                    st.balloons()
                else:
                    st.error("ACCESS DENIED: INVALID KEY OR CORRUPTED SIGNAL.")
            except Exception as e:
                st.error("DECRYPTION ERROR: DATA INTEGRITY COMPROMISED.")
