import streamlit as st
import requests
import io
from PIL import Image
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine

# Initialize
crypto = CryptoEngine()
mapper = MappingEngine()
stego = StegoEngine()

SERVER_URL = "https://vari-crypt-server.onrender.com"

# ==========================================
# 🪐 INTERSTELLAR CINEMATIC THEME
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Interstellar", page_icon="🪐", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: black; overflow: hidden; }
    [data-testid="stAppViewContainer"]::after {
        content: ""; position: fixed; top: 50%; left: 50%; width: 150vw; height: 100vh;
        background: radial-gradient(ellipse at center, rgba(255, 180, 50, 0.12) 0%, transparent 70%);
        transform: translate(-50%, -50%) rotate(-12deg); pointer-events: none; z-index: 0;
    }
    @keyframes hyper-drift { from { background-position: 0 0; } to { background-position: -5000px 2500px; } }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: absolute; top: 0; left: 0; width: 400%; height: 400%;
        background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
        animation: hyper-drift 450s linear infinite; opacity: 0.15; z-index: 0;
    }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.85) !important; backdrop-filter: blur(12px); }
    div.stButton > button { width: 100%; background: transparent; color: #f1c40f; border: 1px solid #f1c40f; letter-spacing: 5px; transition: 0.6s; }
    div.stButton > button:hover { background: #f1c40f; color: black; box-shadow: 0px 0px 40px rgba(241, 196, 15, 0.4); }
    h1, h2, h3 { color: white !important; letter-spacing: 12px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT")
st.markdown("<p style='letter-spacing: 6px; color: #95a5a6; font-size: 12px;'>QUANTUM ENCRYPTION HUB</p>",
            unsafe_allow_html=True)

operation = st.sidebar.radio("SYSTEM NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

# ==========================================
# MODE 1: ENCODE SIGNAL
# ==========================================
if operation == "📡 ENCODE SIGNAL":
    st.subheader("// DATA INPUT")
    text_input = st.text_area("MESSAGE PAYLOAD")
    password_input = st.text_input("AUTHORIZATION KEY", type="password")
    mode = st.selectbox("OBFUSCATION PROTOCOL",
                        ["SYMBOLIC MAPPING", "STEGANOGRAPHY (UPLOAD)", "STEGANOGRAPHY (AUTO-GENERATE)"])

    cover_img_file = None
    if mode == "STEGANOGRAPHY (UPLOAD)":
        cover_img_file = st.file_uploader("SOURCE PNG", type=["png"])

    if st.button("INITIATE TRANSMISSION"):
        if not text_input or not password_input:
            st.warning("PARAMETERS INCOMPLETE.")
        elif len(text_input.split()) > 20:
            st.error("BUFFER OVERFLOW: MAX 20 WORDS.")
        else:
            try:
                # 1. AES Encryption
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = salt + nonce + tag + ciphertext

                # 2. Obfuscation
                if mode == "SYMBOLIC MAPPING":
                    payload_to_send = mapper.map_ciphertext(full_payload, password_input)
                    st.success("SIGNAL MAPPED TO SYMBOLS")
                    st.code(payload_to_send)
                elif mode == "STEGANOGRAPHY (UPLOAD)":
                    if not cover_img_file:
                        st.error("CARRIER IMAGE REQUIRED.")
                        st.stop()
                    payload_to_send = full_payload.hex()
                    stego_bytes = stego.hide_data(cover_img_file, payload_to_send, False)
                    st.image(stego_bytes, caption="ENCRYPTED CARRIER", width=300)
                    st.download_button("DOWNLOAD FILE", stego_bytes, "carrier.png")
                else:  # AUTO-GENERATE
                    payload_to_send = full_payload.hex()
                    stego_bytes = stego.hide_data(None, payload_to_send, True)
                    st.image(stego_bytes, caption="SYSTEM ARTIFACT", width=300)
                    st.download_button("DOWNLOAD ARTIFACT", stego_bytes, "cosmic_artifact.png")

                # 3. Cloud Sync
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": payload_to_send}},
                                    timeout=60)
                st.info(f"LINK ESTABLISHED. MISSION ID: {res.json().get('msg_id')}")

            except Exception as e:
                st.error(f"MISSION FAILURE: {e}")

# ==========================================
# MODE 2: DECODE SIGNAL
# ==========================================
else:
    st.subheader("// SIGNAL RECEPTION")
    st.warning("⚠️ CRITICAL: Signals self-destruct immediately upon extraction.")
    method = st.radio("DECODE SOURCE", ["CLOUD ID", "CARRIER FILE"])
    password = st.text_input("AUTHORIZATION KEY", type="password")

    if method == "CLOUD ID":
        msg_id = st.text_input("MISSION ID")
        if st.button("PULL & PURGE DATA"):
            try:
                res = requests.get(f"{SERVER_URL}/receive/{msg_id}", timeout=60)
                if res.status_code == 200:
                    raw_data = res.json()['visual_data']
                    # Auto-detect if symbols or hex
                    full_bytes = mapper.unmap_ciphertext(raw_data, password) if any(
                        c in raw_data for c in "ΑΒΓΔ") else bytes.fromhex(raw_data)
                    salt, nonce, tag, ciphertext = full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[
                        48:]
                    st.success(f"MESSAGE RECOVERED: {crypto.decrypt_data(salt, nonce, tag, ciphertext, password)}")
                else:
                    st.error("SIGNAL LOST: Data extracted or expired.")
            except Exception as e:
                st.error(f"DECODE ERROR: {e}")

    elif method == "CARRIER FILE":
        steg_file = st.file_uploader("UPLOAD CARRIER", type=["png"])
        if st.button("EXTRACT DATA"):
            try:
                hex_data = stego.reveal_data(steg_file)
                full_bytes = bytes.fromhex(hex_data)
                salt, nonce, tag, ciphertext = full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:]
                st.success(f"MESSAGE RECOVERED: {crypto.decrypt_data(salt, nonce, tag, ciphertext, password)}")
            except Exception as e:
                st.error(f"EXTRACTION FAILED: {e}")
