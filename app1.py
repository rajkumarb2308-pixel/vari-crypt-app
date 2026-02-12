import streamlit as st
import requests
import io
from PIL import Image
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine

# Initialize Engines
crypto = CryptoEngine()
mapper = MappingEngine()
stego = StegoEngine()

SERVER_URL = "https://vari-crypt-server.onrender.com" 

# ==========================================
# 🪐 CINEMATIC INTERSTELLAR UI
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Interstellar", page_icon="🪐", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: black; overflow: hidden; }
    
    /* Gargantua Accretion Disk */
    [data-testid="stAppViewContainer"]::after {
        content: ""; position: fixed; top: 50%; left: 50%; width: 150vw; height: 100vh;
        background: radial-gradient(ellipse at center, rgba(255, 180, 50, 0.12) 0%, transparent 75%);
        transform: translate(-50%, -50%) rotate(-12deg); pointer-events: none; z-index: 0;
    }

    /* Moving Starfield */
    @keyframes hyper-drift { from { background-position: 0 0; } to { background-position: -5000px 2500px; } }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: absolute; top: 0; left: 0; width: 400%; height: 400%;
        background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
        animation: hyper-drift 450s linear infinite; opacity: 0.15; z-index: 0;
    }

    /* Miller's Planet Orbit */
    @keyframes orbit-miller {
        0% { transform: translate(-30vw, 45vh) scale(0.8); }
        50% { transform: translate(110vw, 15vh) scale(1.0); }
        100% { transform: translate(-30vw, 45vh) scale(0.8); }
    }
    .planet-miller {
        position: fixed; width: 420px; height: 420px;
        background: radial-gradient(circle at 35% 35%, #5d9cec 0%, #3bafda 40%, #000 100%);
        border-radius: 50%; opacity: 0.12; filter: blur(5px);
        animation: orbit-miller 380s ease-in-out infinite; pointer-events: none; z-index: 0;
    }

    /* Sidebar & Inputs */
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.9) !important; backdrop-filter: blur(15px); }
    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        background-color: rgba(15, 15, 17, 0.95) !important; color: #ecf0f1 !important;
        font-family: 'Courier New', monospace; border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    div.stButton > button { width: 100%; background: transparent; color: #f1c40f; border: 1px solid #f1c40f; letter-spacing: 5px; transition: 0.6s; }
    div.stButton > button:hover { background: #f1c40f; color: black; box-shadow: 0px 0px 45px rgba(241, 196, 15, 0.5); }
    h1, h2, h3 { color: white !important; letter-spacing: 12px; text-transform: uppercase; }
    </style>
    <div class="planet-miller"></div>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT")
operation = st.sidebar.radio("SYSTEM NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

# ==========================================
# 📡 MODE 1: ENCODE SIGNAL
# ==========================================
if operation == "📡 ENCODE SIGNAL":
    st.subheader("// DATA INPUT")
    text_input = st.text_area("MESSAGE PAYLOAD")
    password_input = st.text_input("AUTHORIZATION KEY", type="password")
    mode = st.selectbox("OBFUSCATION PROTOCOL", ["SYMBOLIC MAPPING", "STEGANOGRAPHY (UPLOAD)", "STEGANOGRAPHY (AUTO-GENERATE)"])

    if mode == "STEGANOGRAPHY (UPLOAD)":
        # UPDATED: Now accepts PNG, JPG, and JPEG
        cover_file = st.file_uploader("SOURCE IMAGE (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
        if cover_file and st.button("INITIATE TRANSMISSION"):
            try:
                # AES Encryption
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = (salt + nonce + tag + ciphertext).hex()
                
                # Stego Hiding (Works for JPG/PNG -> Outputs PNG)
                stego_bytes = stego.hide_data(cover_file, full_payload, False)
                st.download_button("DOWNLOAD ENCRYPTED PNG", stego_bytes, "carrier.png")
                
                # Cloud Sync
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": full_payload}}, timeout=60)
                st.info(f"MISSION ESTABLISHED. ID: {res.json().get('msg_id')}")
            except Exception as e: st.error(f"FAILURE: {e}")
            
    elif mode == "STEGANOGRAPHY (AUTO-GENERATE)":
        if st.button("GENERATE & TRANSMIT"):
            try:
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = (salt + nonce + tag + ciphertext).hex()
                
                stego_bytes = stego.hide_data(None, full_payload, True)
                st.image(stego_bytes, caption="SYSTEM ARTIFACT", width=350)
                st.download_button("DOWNLOAD ARTIFACT", stego_bytes, "cosmic_artifact.png")
                
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": full_payload}}, timeout=60)
                st.info(f"MISSION ESTABLISHED. ID: {res.json().get('msg_id')}")
            except Exception as e: st.error(f"FAILURE: {e}")

    else: # SYMBOLIC MAPPING
        if st.button("MAP & TRANSMIT"):
            try:
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = salt + nonce + tag + ciphertext
                output = mapper.map_ciphertext(full_payload, password_input)
                st.code(output)
                
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": output}}, timeout=60)
                st.info(f"MISSION ESTABLISHED. ID: {res.json().get('msg_id')}")
            except Exception as e: st.error(f"FAILURE: {e}")

# ==========================================
# 📥 MODE 2: DECODE SIGNAL
# ==========================================
else:
    st.subheader("// SIGNAL RECEPTION")
    st.warning("⚠️ CRITICAL: Cloud signals self-destruct immediately upon extraction.")
    
    method = st.radio("DECODE SOURCE", ["CLOUD ID (PULL & PURGE)", "MANUAL SYMBOLS", "CARRIER FILE (STEGO)"])
    password = st.text_input("AUTHORIZATION KEY", type="password")

    if method == "CLOUD ID (PULL & PURGE)":
        msg_id = st.text_input("MISSION ID")
        if st.button("PULL DATA"):
            try:
                res = requests.get(f"{SERVER_URL}/receive/{msg_id}", timeout=60)
                if res.status_code == 200:
                    raw_data = res.json()['visual_data']
                    full_bytes = mapper.unmap_ciphertext(raw_data, password) if any(c in raw_data for c in "ΑΒΓΔ") else bytes.fromhex(raw_data)
                    st.success(f"RECOVERED: {crypto.decrypt_data(full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:], password)}")
                else: st.error("SIGNAL LOST.")
            except Exception as e: st.error(f"ERROR: {e}")

    elif method == "CARRIER FILE (STEGO)":
        # UPDATED: Decoder also accepts JPG and PNG
        steg_file = st.file_uploader("UPLOAD CARRIER (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
        if st.button("REVEAL SIGNAL"):
            if steg_file:
                try:
                    hex_data = stego.reveal_data(steg_file)
                    full_bytes = bytes.fromhex(hex_data)
                    st.success(f"RECOVERED: {crypto.decrypt_data(full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:], password)}")
                except Exception as e: st.error(f"EXTRACTION FAILED: {e}")
            else:
                st.warning("Please upload a file first.")
