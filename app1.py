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
# 🌌 CINEMATIC INTERSTELLAR UI
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Interstellar", page_icon="🪐", layout="wide")

st.markdown("""
    <style>
    /* 1. The Deep Void & Gravitational Lensing */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a0a0c 0%, #000000 100%);
        overflow: hidden;
    }

    /* Accretion Disk Glow (Gargantua Style) */
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        top: 50%; left: 50%;
        width: 160vw; height: 120vh;
        background: radial-gradient(ellipse at center, 
                    rgba(255, 165, 0, 0.08) 0%, 
                    rgba(255, 69, 0, 0.03) 35%, 
                    transparent 75%);
        transform: translate(-50%, -50%) rotate(-15deg);
        pointer-events: none;
        z-index: 0;
    }

    /* 2. Layered Starfield (Parallax Drift) */
    @keyframes star-drift {
        from { background-position: 0 0; }
        to { background-position: -10000px 5000px; }
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 400%; height: 400%;
        background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
        animation: star-drift 500s linear infinite;
        opacity: 0.25;
        z-index: 0;
    }

    /* 3. Miller's Planet (Water Giant) Motion */
    @keyframes orbit-miller {
        0% { transform: translate(-30vw, 40vh) scale(0.9); }
        50% { transform: translate(110vw, 15vh) scale(1.1); }
        100% { transform: translate(-30vw, 40vh) scale(0.9); }
    }

    .planet-miller {
        position: fixed;
        width: 450px; height: 450px;
        background: radial-gradient(circle at 35% 35%, #5d9cec 0%, #3bafda 30%, #000 100%);
        border-radius: 50%;
        opacity: 0.12;
        filter: blur(4px);
        animation: orbit-miller 350s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
        box-shadow: -20px -20px 80px rgba(0,0,0,0.8) inset;
    }

    /* 4. Endurance-Style Holographic Interface */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
    }

    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        background-color: rgba(15, 15, 17, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #dcdde1 !important;
        font-family: 'Courier New', monospace;
    }

    /* Tactical Orange Accent Buttons */
    div.stButton > button {
        width: 100%;
        background: transparent;
        color: #e67e22;
        border: 1px solid #e67e22;
        border-radius: 1px;
        text-transform: uppercase;
        letter-spacing: 5px;
        font-weight: 100;
        transition: 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    div.stButton > button:hover {
        background: #e67e22;
        color: black;
        box-shadow: 0px 0px 35px rgba(230, 126, 34, 0.4);
    }

    h1, h2, h3 {
        color: #f5f6fa !important;
        font-weight: 100 !important;
        letter-spacing: 12px !important;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(255,255,255,0.1);
    }
    </style>

    <div class="planet-miller"></div>
    """, unsafe_allow_html=True)

# ==========================================
# 🛰️ MISSION CONTROL UI
# ==========================================
st.title("VARI-CRYPT")
st.markdown(
    "<p style='letter-spacing: 7px; color: #7f8c8d; font-size: 11px; margin-top: -20px;'>SECURE COGNITIVE TRANSMISSION</p>",
    unsafe_allow_html=True)

operation = st.sidebar.radio("SYSTEM NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])

if operation == "📡 ENCODE SIGNAL":
    st.subheader("// DATA INPUT")
    text_input = st.text_area("MESSAGE PAYLOAD")
    password_input = st.text_input("AUTHORIZATION KEY", type="password")
    mode = st.selectbox("OBFUSCATION PROTOCOL",
                        ["SYMBOLIC MAPPING", "STEGANOGRAPHY (UPLOAD)", "STEGANOGRAPHY (AUTO-GENERATE)"])

    if st.button("INITIATE TRANSMISSION"):
        if not text_input or not password_input:
            st.warning("PARAMETERS INCOMPLETE.")
        else:
            try:
                salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)
                full_payload = salt + nonce + tag + ciphertext

                if mode == "SYMBOLIC MAPPING":
                    payload_to_send = mapper.map_ciphertext(full_payload, password_input)
                    st.success("SIGNAL MAPPED")
                    st.code(payload_to_send)
                elif mode == "STEGANOGRAPHY (UPLOAD)":
                    payload_to_send = full_payload.hex()
                    # User would upload file here
                    st.info("Ensure you have selected the carrier file.")
                else:  # AUTO-GENERATE
                    payload_to_send = full_payload.hex()
                    stego_bytes = stego.hide_data(None, payload_to_send, True)
                    st.image(stego_bytes, caption="GENERATED NEBULA CARRIER", width=350)
                    st.download_button("EXTRACT ARTIFACT", stego_bytes, "cosmic_data.png")

                # Cloud Sync
                res = requests.post(f"{SERVER_URL}/send", json={"encrypted_payload": {"visual_data": payload_to_send}},
                                    timeout=60)
                st.info(f"MISSION ESTABLISHED. ID: {res.json().get('msg_id')}")
            except Exception as e:
                st.error(f"FAILURE: {e}")

else:
    st.subheader("// SIGNAL RECEPTION")
    st.warning("⚠️ CRITICAL: Signals self-destruct immediately upon extraction.")
    msg_id = st.text_input("MISSION ID")
    password = st.text_input("AUTHORIZATION KEY", type="password")

    if st.button("PULL & PURGE DATA"):
        try:
            res = requests.get(f"{SERVER_URL}/receive/{msg_id}", timeout=60)
            if res.status_code == 200:
                raw_data = res.json()['visual_data']
                full_bytes = mapper.unmap_ciphertext(raw_data, password) if any(
                    c in raw_data for c in "ΑΒΓΔ") else bytes.fromhex(raw_data)
                salt, nonce, tag, ciphertext = full_bytes[:16], full_bytes[16:32], full_bytes[32:48], full_bytes[48:]
                st.success(f"RECOVERED: {crypto.decrypt_data(salt, nonce, tag, ciphertext, password)}")
            else:
                st.error("SIGNAL LOST: Data expired or previously read.")
        except Exception as e:
            st.error(f"DECODE ERROR: {e}")
