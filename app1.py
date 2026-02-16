import streamlit as st
import requests
import io
import os
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
# 🌌 THEME: ENHANCED NEBULA (UI ONLY)
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Event Horizon", page_icon="🌌", layout="wide")

st.markdown("""
    <style>
    /* 1. BACKGROUND: MOVING NEBULA */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2011&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        animation: cosmic-drift 80s ease-in-out infinite alternate;
    }

    /* 2. SPECIAL EFFECTS: TWINKLING STARDUST */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 1px, transparent 2px),
            radial-gradient(white, rgba(255,255,255,.15) 1.5px, transparent 2.5px);
        background-size: 450px 450px, 250px 250px;
        opacity: 0.5;
        animation: stardust-twinkle 8s linear infinite;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes cosmic-drift {
        0% { background-position: 45% 50%; transform: scale(1); }
        100% { background-position: 55% 55%; transform: scale(1.08); }
    }

    @keyframes stardust-twinkle {
        0% { opacity: 0.3; transform: translateY(0); }
        50% { opacity: 0.7; }
        100% { opacity: 0.3; transform: translateY(-30px); }
    }

    /* 3. STATIC GLASS UI */
    div.stButton > button { 
        width: 100%; background: rgba(0, 0, 0, 0.4); color: #00ffff; 
        border: 1px solid rgba(0, 255, 255, 0.4); font-weight: bold;
        letter-spacing: 2px; backdrop-filter: blur(5px);
    }
    div.stButton > button:hover { 
        background: rgba(0, 255, 255, 0.2); 
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.6); 
        border-color: #fff;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        background-color: rgba(0, 0, 0, 0.5) !important; color: #ffffff !important; 
        border: 1px solid rgba(0, 255, 255, 0.2) !important; 
        backdrop-filter: blur(10px);
    }

    h1 { color: #fff !important; text-shadow: 0 0 25px #e100ff, 0 0 10px #00ffff; text-align: center; }
    h3, label { color: #ffffff !important; text-shadow: 0 0 8px #000; }

    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px) saturate(150%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT: EVENT HORIZON")

# ==========================================
# 🛰️ MISSION CONTROL (NO LOGIN REQUIRED)
# ==========================================

with st.sidebar:
    st.markdown("### 👨‍🚀 STATUS: `ACTIVE`")
    op = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

if op == "📡 ENCODE SIGNAL":
    st.subheader("// GENERATE SECURE TRANSMISSION")
    msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)")
    pwd = st.text_input("ENCRYPTION KEY", type="password")

    mode = st.selectbox("PROTOCOL",
                        ["WILDLIFE AUTO-GEN (IMAGE)", "EMOJI MAPPING", "MANUAL IMAGE UPLOAD", "AUDIO ENCRYPTION"])

    up_file = None
    if "MANUAL" in mode:
        up_file = st.file_uploader("UPLOAD IMAGE", type=["png", "jpg"])
    elif "AUDIO" in mode:
        up_file = st.file_uploader("UPLOAD AUDIO", type=["wav", "mp3"])

    if st.button("SEND SIGNAL"):
        try:
            s, n, t, c = st.session_state.crypto.encrypt_data(msg, pwd)
            f_hex = (s + n + t + c).hex()

            if "EMOJI" in mode:
                output = st.session_state.mapper.map_ciphertext(bytes.fromhex(f_hex), pwd)
                st.code(output, language="text")
                sync_data = output
            elif "WILDLIFE" in mode:
                data = st.session_state.stego.hide_data(None, f_hex, use_wildlife=True)
                st.image(data, caption="WILDLIFE ARTIFACT")
                st.download_button("SAVE", data, "wildlife.png")
                sync_data = f_hex
            elif "MANUAL" in mode and up_file:
                data = st.session_state.stego.hide_data(up_file, f_hex)
                st.image(data)
                st.download_button("SAVE", data, "mission.png")
                sync_data = f_hex
            elif "AUDIO" in mode and up_file:
                data = st.session_state.audio_stego.hide_data(up_file, f_hex)
                st.audio(data)
                st.download_button("SAVE", data, "signal.wav")
                sync_data = f_hex

            res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": sync_data}})
            if res.status_code == 200:
                st.info(f"MISSION ID: {res.json().get('msg_id')}")
            st.success("TRANSMITTED.")
        except Exception as e:
            st.error(f"FAIL: {e}")

else:
    st.subheader("// RECOVER SIGNAL")
    method = st.radio("SOURCE TYPE", ["CLOUD MISSION ID", "MANUAL EMOJI SYMBOLS", "IMAGE FILE", "AUDIO FILE"])
    k = st.text_input("DECRYPT KEY", type="password")

    extracted_hex = None

    if method == "CLOUD MISSION ID":
        mid = st.text_input("MISSION ID")
        if st.button("PULL DATA") and mid:
            res = requests.get(f"{SERVER_URL}/receive/{mid}")
            if res.status_code == 200:
                raw_data = res.json()['visual_data']
                extracted_hex = st.session_state.mapper.unmap_ciphertext(raw_data, k).hex() if any(
                    c in raw_data for c in "ΑΒΓΔ") else raw_data
            else:
                st.error("NOT FOUND.")

    elif method == "MANUAL EMOJI SYMBOLS":
        emoji_input = st.text_area("PASTE SYMBOLS")
        if st.button("TRANSLATE"):
            extracted_hex = st.session_state.mapper.unmap_ciphertext(emoji_input, k).hex()

    elif method == "IMAGE FILE":
        up_file = st.file_uploader("UPLOAD ARTIFACT", type=["png", "jpg"])
        if st.button("SCAN") and up_file:
            extracted_hex = st.session_state.stego.reveal_data(up_file)

    elif method == "AUDIO FILE":
        up_file = st.file_uploader("UPLOAD SIGNAL", type=["wav", "mp3"])
        if st.button("ANALYZE") and up_file:
            extracted_hex = st.session_state.audio_stego.reveal_data(up_file)

    if extracted_hex:
        try:
            b = bytes.fromhex(extracted_hex)
            dec = st.session_state.crypto.decrypt_data(b[:16], b[16:32], b[32:48], b[48:], k)
            st.success(f"🔓 RECOVERED: {dec}")
            st.balloons()
        except:
            st.error("DECRYPTION FAILED.")
