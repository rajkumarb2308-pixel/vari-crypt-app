import streamlit as st
import sqlite3
import hashlib
import random
import string
import requests
import io
import os
import math
from PIL import Image

# --- V1 ENGINES (Original) ---
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine
from stego_engine import StegoEngine
from audio_engine import AudioStego

# --- V2 ENGINES (Heavy-Duty Enhancements) ---
from enhanced_mapping import EnhancedMapping
from enhanced_stego import EnhancedImageStego
from enhanced_audio import EnhancedAudioStego
from cover_engine import AquaticCoverEngine

# Set up a temporary directory for V2 file processing
os.makedirs("temp_uploads", exist_ok=True)

# Broad acceptance arrays for all media
ALL_IMAGES = ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff']
ALL_AUDIO = ['wav', 'mp3', 'ogg', 'm4a', 'flac', 'aac']

# ==========================================
# ⚙️ 1. FLEXIBLE AUTHENTICATION
# ==========================================
DB_FILE = "vari_crypt_v2.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (identifier TEXT PRIMARY KEY, password TEXT)''')
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


init_db()

# ==========================================
# ⚙️ 2. ENGINE INITIALIZATION
# ==========================================
if 'engines_loaded' not in st.session_state:
    st.session_state.crypto = CryptoEngine()
    st.session_state.mapper = MappingEngine()
    st.session_state.stego = StegoEngine()
    st.session_state.audio_stego = AudioStego()
    # V2 INIT
    st.session_state.mapper_v2 = EnhancedMapping()
    st.session_state.stego_v2 = EnhancedImageStego()
    st.session_state.audio_v2 = EnhancedAudioStego()
    st.session_state.cover_gen = AquaticCoverEngine()
    st.session_state.engines_loaded = True

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
    div.stButton > button { width: 100%; background: rgba(0, 0, 0, 0.4); color: #00ffff; border: 1px solid rgba(0, 255, 255, 0.4); font-weight: bold; backdrop-filter: blur(5px); }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { background-color: rgba(0, 0, 0, 0.5) !important; color: #ffffff !important; border: 1px solid rgba(0, 255, 255, 0.2) !important; backdrop-filter: blur(10px); }
    h1 { color: #fff !important; text-shadow: 0 0 25px #e100ff, 0 0 10px #00ffff; text-align: center; }
    h3, label { color: #ffffff !important; text-shadow: 0 0 8px #000; }
    section[data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.7) !important; backdrop-filter: blur(15px); }
    </style>
    """, unsafe_allow_html=True)

st.title("VARI-CRYPT: EVENT HORIZON")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None
if 'verified_id' not in st.session_state: st.session_state.verified_id = None

# ==========================================
# 🚀 MAIN LOGIC: GATEKEEPER
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>AUTHENTICATION REQUIRED</h3>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🔑 LOGIN", "📝 REGISTER", "❓ RESET PASS"])

        with tab1:
            l_id = st.text_input("Email OR Phone Number", key="l_id")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("LOGIN", key="btn_login"):
                user = get_user(l_id)
                if user and verify_password(user[1], l_pass):
                    st.session_state.logged_in = True
                    st.session_state.user_email = l_id
                    st.rerun()
                else:
                    st.error("INVALID CREDENTIALS")

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
# 🛰️ MISSION CONTROL
# ==========================================
else:
    with st.sidebar:
        st.markdown(f"### 👨‍🚀 PILOT: `{st.session_state.user_email}`")
        st.markdown("---")
        op = st.radio("NAVIGATION", ["📡 ENCODE SIGNAL", "📥 DECODE SIGNAL"])
        engine_version = st.radio("SYSTEM ENGINE", ["📝 V1: TEXT PAYLOAD", "📁 V2: MEDIA PAYLOAD"])
        st.markdown("---")
        if st.button("LOGOUT / EJECT"):
            st.session_state.logged_in = False
            st.rerun()

    # ------------------------------------------
    # ENCODE
    # ------------------------------------------
    if op == "📡 ENCODE SIGNAL":
        if engine_version == "📝 V1: TEXT PAYLOAD":
            st.subheader("// GENERATE SECURE TEXT TRANSMISSION")
            msg = st.text_area("PAYLOAD DATA (MAX 20 WORDS)")
            pwd = st.text_input("ENCRYPTION KEY", type="password")
            mode = st.selectbox("PROTOCOL", ["WILDLIFE AUTO-GEN (IMAGE)", "EMOJI MAPPING", "MANUAL IMAGE UPLOAD",
                                             "AUDIO ENCRYPTION"])

            up_file = None
            if "MANUAL" in mode:
                up_file = st.file_uploader("UPLOAD IMAGE", type=["png", "jpg"])
            elif "AUDIO" in mode:
                up_file = st.file_uploader("UPLOAD AUDIO", type=["wav", "mp3"])

            if st.button("SEND SIGNAL (V1)"):
                try:
                    s, n, t, c = st.session_state.crypto.encrypt_data(msg, pwd)
                    f_hex = (s + n + t + c).hex()

                    if "EMOJI" in mode:
                        output = st.session_state.mapper.map_ciphertext(bytes.fromhex(f_hex), pwd)
                        st.code(output, language="text")
                    elif "WILDLIFE" in mode:
                        data = st.session_state.stego.hide_data(None, f_hex, use_wildlife=True)
                        st.image(data, caption="WILDLIFE ARTIFACT")
                        st.download_button("SAVE", data, "wildlife.png")
                    elif "MANUAL" in mode and up_file:
                        data = st.session_state.stego.hide_data(up_file, f_hex)
                        st.image(data)
                        st.download_button("SAVE", data, "mission.png")
                    elif "AUDIO" in mode and up_file:
                        data = st.session_state.audio_stego.hide_data(up_file, f_hex)
                        st.audio(data)
                        st.download_button("SAVE", data, "signal.wav")

                    st.success("SIGNAL GENERATED SUCCESSFULLY.")

                except Exception as e:
                    st.error(f"FAIL: {e}")

        elif engine_version == "📁 V2: MEDIA PAYLOAD":
            st.subheader("// GENERATE HIGH-CAPACITY MEDIA TRANSMISSION")

            sec_file = st.file_uploader("UPLOAD SECRET PAYLOAD (MAX 200MB)", type=None, key="v2_sec")
            pwd_v2 = st.text_input("V2 ENCRYPTION KEY", type="password")
            mode_v2 = st.selectbox("V2 PROTOCOL", ["AQUATIC AUTO-GEN (IMAGE)", "EMOJI COMPRESSION", "2-BIT IMAGE STEGO",
                                                   "AUDIO STEGO"])

            cov_file = None
            if mode_v2 in ["2-BIT IMAGE STEGO", "AUDIO STEGO"]:
                if "IMAGE" in mode_v2:
                    cov_file = st.file_uploader("UPLOAD COVER IMAGE", type=None, key="v2_img")
                elif "AUDIO" in mode_v2:
                    cov_file = st.file_uploader("UPLOAD COVER AUDIO", type=None, key="v2_aud")

            if st.button("SEND SIGNAL (V2)"):
                if not sec_file:
                    st.warning("PLEASE UPLOAD A SECRET PAYLOAD.")
                elif not pwd_v2:
                    st.warning("PLEASE ENTER YOUR V2 ENCRYPTION KEY.")
                elif mode_v2 in ["2-BIT IMAGE STEGO", "AUDIO STEGO"] and not cov_file:
                    st.warning("PLEASE UPLOAD A COVER FILE FOR THIS PROTOCOL.")
                else:
                    sec_path = os.path.join("temp_uploads", f"sec_{sec_file.name}")
                    with open(sec_path, "wb") as f:
                        f.write(sec_file.getbuffer())

                    try:
                        with st.spinner("ENGAGING OPTIMIZED V2 PROTOCOLS..."):

                            if mode_v2 == "EMOJI COMPRESSION":
                                out = st.session_state.mapper_v2.compress_and_map(sec_path, pwd_v2)
                                display_text = out[
                                                   :300] + "\n\n... [DATA TRUNCATED TO PREVENT BROWSER CRASH. DOWNLOAD FULL CIPHER BELOW] ..."
                                st.code(display_text, language="text")

                                out_txt_path = os.path.join("temp_uploads", "v2_emoji_cipher.txt")
                                with open(out_txt_path, "w", encoding="utf-8") as f:
                                    f.write(out)

                                with open(out_txt_path, "rb") as file:
                                    st.download_button("SAVE V2 EMOJI CIPHER (.txt)", data=file,
                                                       file_name="v2_emoji_cipher.txt")
                                st.success("PAYLOAD SECURED, COMPRESSED, AND MAPPED.")

                            elif mode_v2 == "AQUATIC AUTO-GEN (IMAGE)":
                                cov_path = os.path.join("temp_uploads", "generated_cover.jpg")

                                # 1. Calculate the mathematical minimum size required for the payload
                                payload_bytes = os.path.getsize(sec_path)
                                required_pixels = int((payload_bytes * 1.5) / 0.75) + 10000
                                min_side = max(1080, math.ceil(math.sqrt(required_pixels)))

                                try:
                                    # 2. Fetch limitless internet image AT the requested size
                                    cover_url = st.session_state.cover_gen.generate_cover(min_side)

                                    # Browser-spoofing to prevent the internet host from blocking the request
                                    headers = {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

                                    # Increased timeout to 8 seconds to allow large dynamic images to download
                                    cover_response = requests.get(cover_url, headers=headers, timeout=8)

                                    if cover_response.status_code == 200:
                                        with open(cov_path, "wb") as f:
                                            f.write(cover_response.content)
                                        # Verify it is a real image, not an HTML error page
                                        Image.open(cov_path).verify()
                                    else:
                                        raise ValueError("Web request blocked or failed.")

                                except Exception as e:
                                    # 3. FALLBACK: Zero-internet professional gradient
                                    st.warning(f"Internet fetch delayed. Generating secure local aquatic cover...")
                                    fallback = Image.new('RGB', (min_side, min_side),
                                                         color=(0, 25, random.randint(60, 120)))
                                    from PIL import ImageDraw

                                    draw = ImageDraw.Draw(fallback)
                                    for i in range(0, min_side, 20):
                                        draw.line([(0, i), (min_side, i)], fill=(0, 40, random.randint(80, 150)),
                                                  width=8)
                                    fallback.save(cov_path)

                                # 4. Execute the V2 Matrix Injection
                                out_path = os.path.join("temp_uploads", "v2_aquatic_secure.png")
                                st.session_state.stego_v2.hide_data(cov_path, sec_path, out_path, pwd_v2)

                                st.image(out_path, caption="V2 SECURE AQUATIC ARTIFACT")
                                with open(out_path, "rb") as file:
                                    st.download_button("SAVE V2 ARTIFACT", data=file, file_name="v2_aquatic_secure.png")
                                st.success("SECURE DATA INJECTED INTO AQUATIC COVER.")

                            elif mode_v2 == "2-BIT IMAGE STEGO":
                                cov_path = os.path.join("temp_uploads", f"cov_{cov_file.name}")
                                out_path = os.path.join("temp_uploads", "v2_secure.png")
                                with open(cov_path, "wb") as f:
                                    f.write(cov_file.getbuffer())

                                st.session_state.stego_v2.hide_data(cov_path, sec_path, out_path, pwd_v2)
                                st.image(out_path, caption="V2 SECURE IMAGE")
                                with open(out_path, "rb") as file:
                                    st.download_button("SAVE V2 ARTIFACT", data=file, file_name="v2_secure.png")
                                st.success("SECURE DATA INJECTED INTO IMAGE.")

                            elif mode_v2 == "AUDIO STEGO":
                                cov_path = os.path.join("temp_uploads", f"cov_{cov_file.name}")
                                out_path = os.path.join("temp_uploads", "v2_secure.wav")
                                with open(cov_path, "wb") as f:
                                    f.write(cov_file.getbuffer())

                                st.session_state.audio_v2.hide_data(cov_path, sec_path, out_path, pwd_v2)
                                st.audio(out_path)
                                with open(out_path, "rb") as file:
                                    st.download_button("SAVE V2 SIGNAL", data=file, file_name="v2_secure.wav")
                                st.success("SECURE DATA INJECTED INTO AUDIO.")

                    except Exception as e:
                        st.error(f"SYSTEM FAILURE: {e}")

    # ------------------------------------------
    # DECODE
    # ------------------------------------------
    else:
        if engine_version == "📝 V1: TEXT PAYLOAD":
            st.subheader("// RECOVER TEXT SIGNAL")
            method = st.radio("SOURCE TYPE", ["MANUAL EMOJI SYMBOLS", "IMAGE FILE", "AUDIO FILE"])
            k = st.text_input("DECRYPT KEY", type="password")
            extracted_hex = None

            if method == "MANUAL EMOJI SYMBOLS":
                emoji_input = st.text_area("PASTE SYMBOLS")
                if st.button("TRANSLATE"): extracted_hex = st.session_state.mapper.unmap_ciphertext(emoji_input,
                                                                                                    k).hex()

            elif method == "IMAGE FILE":
                up_file = st.file_uploader("UPLOAD ARTIFACT", type=["png", "jpg"])
                if st.button("SCAN") and up_file: extracted_hex = st.session_state.stego.reveal_data(up_file)

            elif method == "AUDIO FILE":
                up_file = st.file_uploader("UPLOAD SIGNAL", type=["wav", "mp3"])
                if st.button("ANALYZE") and up_file: extracted_hex = st.session_state.audio_stego.reveal_data(up_file)

            if extracted_hex:
                try:
                    b = bytes.fromhex(extracted_hex)
                    dec = st.session_state.crypto.decrypt_data(b[:16], b[16:32], b[32:48], b[48:], k)
                    st.success(f"🔓 RECOVERED: {dec}")
                    st.balloons()
                except:
                    st.error("DECRYPTION FAILED.")

        elif engine_version == "📁 V2: MEDIA PAYLOAD":
            st.subheader("// RECOVER MEDIA SIGNAL (V2)")

            method_v2 = st.radio("V2 SOURCE TYPE", ["EMOJI COMPRESSION", "IMAGE FILE (2-Bit LSB)", "AUDIO FILE"])
            pwd_v2 = st.text_input("V2 DECRYPT KEY", type="password")

            out_ext = st.text_input("EXPECTED PAYLOAD EXTENSION (e.g. .jpg, .pdf, .txt)", value=".bin",
                                    help="Specify original format to save correctly.")

            up_file_v2 = None
            emoji_pasted_text = ""

            if method_v2 == "EMOJI COMPRESSION":
                emoji_pasted_text = st.text_area("PASTE MULTI-LANGUAGE CIPHER HERE", height=200)
                st.caption("OR Upload a file if the cipher is too large:")
                up_file_v2 = st.file_uploader("UPLOAD EMOJI CIPHER (.txt)", type=["txt"])
            elif method_v2 == "IMAGE FILE (2-Bit LSB)":
                up_file_v2 = st.file_uploader("UPLOAD V2 ARTIFACT", type=None)
            elif method_v2 == "AUDIO FILE":
                up_file_v2 = st.file_uploader("UPLOAD V2 ARTIFACT", type=None)

            if st.button("INITIATE V2 DECODE"):
                if not pwd_v2:
                    st.warning("PLEASE ENTER V2 DECRYPT KEY.")
                elif method_v2 != "EMOJI COMPRESSION" and not up_file_v2:
                    st.warning("PLEASE UPLOAD THE SECURE ARTIFACT.")
                elif method_v2 == "EMOJI COMPRESSION" and not (up_file_v2 or emoji_pasted_text):
                    st.warning("PLEASE PASTE TEXT OR UPLOAD A CIPHER FILE.")
                else:
                    try:
                        with st.spinner("EXTRACTING OPTIMIZED V2 PAYLOAD..."):
                            recovered_bytes = None

                            if method_v2 == "EMOJI COMPRESSION":
                                if up_file_v2:
                                    emoji_text = up_file_v2.getvalue().decode("utf-8")
                                else:
                                    emoji_text = emoji_pasted_text
                                recovered_bytes = st.session_state.mapper_v2.unmap_and_decompress(emoji_text, pwd_v2)

                            elif method_v2 == "IMAGE FILE (2-Bit LSB)" and up_file_v2:
                                file_path = os.path.join("temp_uploads", f"dec_{up_file_v2.name}")
                                with open(file_path, "wb") as f:
                                    f.write(up_file_v2.getbuffer())
                                recovered_bytes = st.session_state.stego_v2.reveal_data(file_path, pwd_v2)

                            elif method_v2 == "AUDIO FILE" and up_file_v2:
                                file_path = os.path.join("temp_uploads", f"dec_{up_file_v2.name}")
                                with open(file_path, "wb") as f:
                                    f.write(up_file_v2.getbuffer())
                                recovered_bytes = st.session_state.audio_v2.reveal_data(file_path, pwd_v2)

                            if recovered_bytes:
                                st.success("🔓 PAYLOAD RECOVERED SUCCESSFULLY!")
                                final_filename = f"recovered_payload{out_ext}"
                                st.download_button("DOWNLOAD RECOVERED FILE", data=recovered_bytes,
                                                   file_name=final_filename)
                                st.balloons()
                            else:
                                st.error("EXTRACTION FAILED. INCORRECT KEY OR DATA CORRUPTION.")
                    except Exception as e:
                        st.error(f"SYSTEM FAILURE: {e}")
