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

SERVER_URL = "https://vari-crypt-server.onrender.com" # Ensure no trailing slash

# ==========================================
# 🪐 CINEMATIC INTERSTELLAR UI
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Interstellar", page_icon="🪐", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: black; overflow: hidden; }
    
    /* Realistic Accretion Disk (Gargantua) */
    [data-testid="stAppViewContainer"]::after {
        content: ""; position: fixed; top: 50%; left: 50%; width: 150vw; height: 100vh;
        background: radial-gradient(ellipse at center, rgba(255, 180, 50, 0.12) 0%, transparent 75%);
        transform: translate(-50%, -50%) rotate(-12deg); pointer-events: none; z-index: 0;
    }

    /* Moving Parallax Starfield */
    @keyframes hyper-drift { from { background-position: 0 0; } to { background-position: -5000px 2500px; } }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: absolute; top: 0; left: 0; width: 400%; height: 400%;
        background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
        animation: hyper-drift 450s linear infinite; opacity: 0.15; z-index: 0;
    }

    /* Miller's Planet Orbital Motion */
    @keyframes orbit-miller {
        0% { transform: translate(-30vw, 40vh) scale(0.8); }
        50% { transform: translate(110vw, 15vh) scale(1.0); }
        100% { transform: translate(-30vw, 40vh) scale(0.8); }
    }
    .planet-miller {
        position: fixed; width: 400px; height: 400px;
        background: radial-gradient(circle at 35% 35%, #5d9cec 0%, #3bafda 40%, #000 100%);
        border-radius: 50%; opacity: 0.1; filter: blur(5px);
        animation: orbit-miller 350s ease-in-out infinite; pointer-events: none; z-index: 0;
    }

    /* Tactical Sidebar & Inputs */
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.9) !important; backdrop-filter: blur(12px); }
    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        background-color: rgba(15, 15, 17, 0.95) !important; color: #ecf0f1 !important;
        font-family: 'Courier New', monospace; border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    div.stButton > button { 
        width: 100%; background: transparent; color: #f1c40f; 
        border: 1px solid #f1c40f; letter-spacing: 5px; transition: 0.6s;
    }
    div.stButton > button:hover { background: #f1c40f; color: black; box-shadow: 0px 0px 40px rgba(241, 196, 15, 0.4); }
    h1, h2, h3 { color: white !important; letter-spacing: 12px; text-transform: uppercase; }
    </style>
    <div class="planet-miller"></div>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT")
st.markdown("<p style='letter-spacing: 7px; color: #95a5a6; font-size: 11px;'>COGNITIVE DATA TRANSMISSION</p>", unsafe_allow_html=True)

operation = st.sidebar.radio("SYSTEM NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

# ==========================================
# 📡 MODE 1: ENCODE SIGNAL
# ==========================================
if operation == "📡 ENCODE SIGNAL":
    st.subheader("// DATA INPUT")
    text_input = st.text_area("MESSAGE PAYLOAD")
    password_input = st.text_input("AUTHORIZATION KEY", type="password")
    mode = st.selectbox("OBFUSCATION PROTOCOL", ["SYMBOLIC MAPPING", "STEGANOGRAPHY (UPLOAD)", "STEGANOGRAPHY (AUTO-GENERATE)"])

    cover_file = None
    if mode == "STEGANOGRAPHY (UPLOAD)":
        cover_file = st.file_uploader("SOURCE PNG", type=["png"])

    if st.button("INITIATE TRANSMISSION"):
        if not text_input or not password_input:
            st.warning("PARAMETERS INCOMPLETE.")
        else:
            try:
                # AES-256 EAX Core
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = salt + nonce + tag + ciphertext
                
                if mode == "SYMBOLIC MAPPING":
                    payload_to_send = mapper.map_ciphertext(full_payload, password_input)
                    st.code(payload_to_send)
                elif mode == "STEGANOGRAPHY (UPLOAD)":
                    if not cover_file: st.error("Image required."); st.stop()
                    payload_to_send = full_payload.hex()
                    stego_bytes = stego.hide_data(cover_file, payload_to_send, False)
                    st.download_button("DOWNLOAD FILE", stego_bytes, "carrier.png")
                else: # AUTO-GENERATE
                    payload_to_send = full_payload.hex()
                    stego_bytes = stego.hide_data(None, payload_to_send, True)
                    st.image(stego_bytes, caption="SYSTEM ARTIFACT", width=300)
                    st.download_button("DOWNLOAD ARTIFACT", stego_bytes, "cosmic_artifact.png")

                # Cloud Synchronization
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": payload_to_send}}, timeout=60)
                st.info(f"LINK ESTABLISHED. MISSION ID: {res.json().get('msg_id')}")
            except Exception as e:
                st.error(f"FAILURE: {e}")

# ==========================================
# 📥 MODE 2: DECODE SIGNAL
# ==========================================
else:
    st.subheader("// SIGNAL RECEPTION")
    st.warning("⚠️ CRITICAL: Cloud signals self-destruct immediately upon extraction.")
    
    # Fully Flexible Decryption Options
    method = st.radio("DECODE SOURCE", ["CLOUD ID (PULL & PURGE)", "MANUAL SYMBOLS", "CARRIER FILE (STEGO)"])
    password = st.text_input("AUTHORIZATION KEY", type="password")

    if method == "CLOUD ID (PULL & PURGE)":
        msg_id = st.text_input("MISSION ID")
        if st.button("PULL DATA"):
            try:
                res = requests.get(f"{SERVER_URL}/receive/{msg_id}", timeout=60)
                if res.status_code == 200:
                    raw_data = res.json()['visual_data']
                    # Auto-detect Symbols vs Hex
                    full_bytes = mapper.unmap_ciphertext(raw_data, password) if any(c in raw_data for c in "ΑΒΓΔ") else bytes.fromhex(raw_data)
                    st.success(f"RECOVERED: {crypto.decrypt_data(full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:], password)}")
                else:
                    st.error("SIGNAL LOST: Data was previously read or has expired.")
            except Exception as e: st.error(f"DECODE ERROR: {e}")

    elif method == "MANUAL SYMBOLS":
        sym_input = st.text_area("PASTE SYMBOLS")
        if st.button("DECODE SYMBOLS"):
            try:
                full_bytes = mapper.unmap_ciphertext(sym_input, password)
                st.success(f"RECOVERED: {crypto.decrypt_data(full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:], password)}")
            except Exception as e: st.error(f"ERROR: {e}")

    elif method == "CARRIER FILE (STEGO)":
        steg_file = st.file_uploader("UPLOAD CARRIER PNG", type=["png"])
        if st.button("REVEAL SIGNAL"):
            try:
                hex_data = stego.reveal_data(steg_file)
                full_bytes = bytes.fromhex(hex_data)
                st.success(f"RECOVERED: {crypto.decrypt_data(full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:], password)}")
            except Exception as e: st.error(f"EXTRACTION FAILED: {e}")
