import streamlit as st
import sqlite3
import hashlib
import random
import string
import requests
import io
import os
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine
from audio_engine import AudioStego

# ==========================================
# ⚙️ 1. FLEXIBLE AUTHENTICATION (Email OR Phone)
# ==========================================
DB_FILE = "vari_crypt_v2.db"


def init_db():
    """Initializes the local SQLite database with flexible identifier."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 'identifier' can store either Email OR Phone
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     identifier
                     TEXT
                     PRIMARY
                     KEY,
                     password
                     TEXT
                 )''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_hash, input_password):
    return stored_hash == hashlib.sha256(input_password.encode()).hexdigest()


def generate_otp():
    return ''.join(random.choices(string.digits, k=4))


def add_user(identifier, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (identifier, password) VALUES (?, ?)",
                  (identifier, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(identifier):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE identifier=?", (identifier,))
    user = c.fetchone()
    conn.close()
    return user


def update_password(identifier, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE identifier=?",
              (hash_password(new_password), identifier))
    conn.commit()
    conn.close()


# Initialize Database
init_db()

# ==========================================
# ⚙️ 2. VARI-CRYPT ENGINES
# ==========================================
if 'engines_loaded' not in st.session_state:
    st.session_state.crypto = CryptoEngine()
    st.session_state.mapper = MappingEngine()
    st.session_state.stego = StegoEngine()
    st.session_state.audio_stego = AudioStego()
    st.session_state.engines_loaded = True

SERVER_URL = "http://127.0.0.1:8000"

# ==========================================
# 🌌 THEME SETUP
# ==========================================
st.set_page_config(page_title="Vari-Crypt: Event Horizon", page_icon="🌌", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2011&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        animation: cosmic-drift 80s ease-in-out infinite alternate;
    }
    @keyframes cosmic-drift { 0% { background-position: 45% 50%; } 100% { background-position: 55% 55%; } }

    div.stButton > button { 
        width: 100%; background: rgba(0, 0, 0, 0.4); color: #00ffff; 
        border: 1px solid rgba(0, 255, 255, 0.4); font-weight: bold; backdrop-filter: blur(5px);
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        background-color: rgba(0, 0, 0, 0.5) !important; color: #ffffff !important; 
        border: 1px solid rgba(0, 255, 255, 0.2) !important; backdrop-filter: blur(10px);
    }
    h1 { color: #fff !important; text-shadow: 0 0 25px #e100ff, 0 0 10px #00ffff; text-align: center; }
    h3, label { color: #ffffff !important; text-shadow: 0 0 8px #000; }
    section[data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.7) !important; backdrop-filter: blur(15px); }
    </style>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT: EVENT HORIZON")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None
if 'verified_id' not in st.session_state: st.session_state.verified_id = None

# ==========================================
# 🚀 MAIN LOGIC: THE GATEKEEPER
# ==========================================

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>AUTHENTICATION REQUIRED</h3>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🔑 LOGIN", "📝 REGISTER", "❓ RESET PASS"])

        # --- LOGIN TAB ---
        with tab1:
            l_id = st.text_input("Email OR Phone Number", key="l_id")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("LOGIN", key="btn_login"):
                # Check DB for whatever they typed (Email or Phone)
                user = get_user(l_id)
                if user and verify_password(user[1], l_pass):
                    st.session_state.logged_in = True
                    st.session_state.user_email = l_id
                    st.rerun()
                else:
                    st.error("INVALID CREDENTIALS")

        # --- REGISTER TAB ---
        with tab2:
            r_id = st.text_input("Enter Email OR Phone Number", key="r_id")
            r_pass = st.text_input("Create Password", type="password", key="r_pass")

            if st.button("SEND OTP", key="btn_otp"):
                if r_id and r_pass:
                    if get_user(r_id):
                        st.error("USER ALREADY EXISTS.")
                    else:
                        otp = generate_otp()
                        st.session_state.generated_otp = otp
                        st.session_state.otp_sent = True
                        st.info(f"📨 OTP SENT TO {r_id}: {otp}")
                else:
                    st.warning("Please enter details first.")

            if st.session_state.otp_sent:
                otp_input = st.text_input("Enter OTP", key="r_otp_input")
                if st.button("VERIFY & REGISTER", key="btn_register"):
                    if otp_input == st.session_state.generated_otp:
                        if add_user(r_id, r_pass):
                            st.success("ACCOUNT CREATED! PLEASE LOGIN.")
                            st.session_state.otp_sent = False
                        else:
                            st.error("REGISTRATION FAILED.")
                    else:
                        st.error("INVALID OTP.")

        # --- FORGOT PASS TAB ---
        with tab3:
            if not st.session_state.verified_id:
                f_id = st.text_input("Registered Email OR Phone", key="f_id")
                if st.button("FIND ACCOUNT"):
                    if get_user(f_id):
                        st.session_state.verified_id = f_id
                        otp = generate_otp()
                        st.session_state.generated_otp = otp
                        st.info(f"📨 OTP SENT TO {f_id}: {otp}")
                    else:
                        st.error("ACCOUNT NOT FOUND.")
            else:
                st.write(f"Resetting password for: **{st.session_state.verified_id}**")
                f_otp = st.text_input("Enter OTP", key="f_otp_input")
                new_pass = st.text_input("New Password", type="password", key="n_pass")
                if st.button("RESET PASSWORD"):
                    if f_otp == st.session_state.generated_otp:
                        update_password(st.session_state.verified_id, new_pass)
                        st.success("PASSWORD UPDATED! GO TO LOGIN.")
                        st.session_state.verified_id = None
                        st.session_state.generated_otp = None
                    else:
                        st.error("WRONG OTP.")

# ==========================================
# 🛰️ MISSION CONTROL (LOGGED IN)
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍🚀 PILOT: `{st.session_state.user_email}`")
        op = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])
        if st.button("LOGOUT / EJECT"):
            st.session_state.logged_in = False
            st.rerun()

    if op == "📡 ENCODE SIGNAL":
        st.subheader("// GENERATE SECURE TRANSMISSION")
        msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)")
        pwd = st.text_input("ENCRYPTION KEY", type="password")

        # ⚠️ EMOJI MAPPING IS INCLUDED HERE
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

                # --- EMOJI MAPPING LOGIC ---
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
        # ⚠️ MANUAL EMOJI DECODE IS INCLUDED HERE
        method = st.radio("SOURCE TYPE", ["CLOUD MISSION ID", "MANUAL EMOJI SYMBOLS", "IMAGE FILE", "AUDIO FILE"])
        k = st.text_input("DECRYPT KEY", type="password")
        extracted_hex = None

        if method == "CLOUD MISSION ID":
            mid = st.text_input("MISSION ID")
            if st.button("PULL DATA") and mid:
                res = requests.get(f"{SERVER_URL}/receive/{mid}")
                if res.status_code == 200:
                    raw_data = res.json()['visual_data']
                    # Auto-detect if data is Emoji or Hex
                    extracted_hex = st.session_state.mapper.unmap_ciphertext(raw_data, k).hex() if any(
                        c in raw_data for c in "ΑΒΓΔ") else raw_data
                else:
                    st.error("NOT FOUND.")

        # --- EMOJI DECODE LOGIC ---
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
