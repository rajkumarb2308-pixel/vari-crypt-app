import streamlit as st
import requests
from crypto_engine import CryptoEngine
from mapping_engine import MappingEngine

crypto = CryptoEngine()
mapper = MappingEngine()

SERVER_URL = "https://vari-crypt-app.onrender.com"

st.set_page_config(page_title="Vari-Crypt", page_icon="🔐", layout="centered")

st.title("🔐 Vari-Crypt Secure Messaging")
st.markdown("### AES-256 + Visual Obfuscation + Cloud [cite: 16]")

operation = st.sidebar.radio("Select Operation", ["Encrypt & Send", "Retrieve & Decrypt"])

# ==========================================
# ENCRYPT & SEND
# ==========================================
if operation == "Encrypt & Send":
    st.subheader("Send Secure Message")
    # Enforce optimized real-time processing limit [cite: 28]
    text_input = st.text_area("Enter Message (Max 20 words)")
    password_input = st.text_input("Enter Password", type="password")

    if st.button("Encrypt & Process"):
        if not text_input.strip() or not password_input.strip():
            st.warning("Message and password are required.")
            st.stop()

        # Strict 0-20 word limit constraint [cite: 28]
        if len(text_input.split()) > 20:
            st.error("Maximum 20 words allowed.")
            st.stop()

        try:
            salt, nonce, tag, ciphertext = crypto.encrypt_data(text_input, password_input)

            # Bundle entire encrypted package
            full_payload = salt + nonce + tag + ciphertext
            visual_cipher = mapper.map_ciphertext(full_payload, password_input)

            st.markdown("---")
            st.subheader("✨ Generated Visual Cipher")
            st.info("Standalone encrypted package. Copy and share manually.")
            st.code(visual_cipher, language=None)

            # Transmit visual data to server [cite: 29]
            response = requests.post(
                f"{SERVER_URL}/send",
                json={"encrypted_payload": {"visual_data": visual_cipher}},
                timeout=10
            )

            if response.status_code == 200:
                msg_id = response.json().get("message_id")
                st.success("Uploaded to Database!")
                st.code(f"Message ID: {msg_id}")
            else:
                st.error("Upload failed. Use the manual visual cipher above.")

        except Exception as e:
            st.error(f"Error: {e}. Is the server running?")

# ==========================================
# RETRIEVE & DECRYPT
# ==========================================
elif operation == "Retrieve & Decrypt":
    st.subheader("Retrieve Secure Message")
    tab1, tab2 = st.tabs(["☁️ Fetch from Cloud (ID)", "📋 Manual Paste (Symbols)"])


    def process_decryption(visual_string, password):
        try:
            full_payload = mapper.unmap_ciphertext(visual_string, password)
            if len(full_payload) < 48:
                st.error("Data corrupted: Payload too short.")
                return

            # Extract headers from the bundled package
            salt = full_payload[:16]
            nonce = full_payload[16:32]
            tag = full_payload[32:48]
            ciphertext = full_payload[48:]

            # Retrieve original text using receiver steps [cite: 36]
            original_text = crypto.decrypt_data(salt, nonce, tag, ciphertext, password)

            if "ERROR" in original_text:
                st.error(original_text)  # Detects even a single symbol change [cite: 56]
            else:
                st.success("Decryption Successful!")
                st.info(original_text)
        except Exception as e:
            st.error(f"Decryption failed: Check password or data integrity. Error: {e}")


    with tab1:
        msg_id = st.text_input("Enter Message ID")
        pwd_cloud = st.text_input("Password (Cloud)", type="password", key="p1")
        if st.button("Fetch & Decrypt ID"):
            if msg_id and pwd_cloud:
                try:
                    res = requests.get(f"{SERVER_URL}/receive/{msg_id}", timeout=10)
                    if res.status_code == 200:
                        process_decryption(res.json()["visual_data"], pwd_cloud)
                    else:
                        st.error("Message not found.")
                except:
                    st.error("Failed to connect to server.")

    with tab2:
        manual_symbols = st.text_area("Paste Visual Cipher")
        pwd_manual = st.text_input("Password (Manual)", type="password", key="p2")
        if st.button("Decrypt Manually"):
            if manual_symbols and pwd_manual:

                process_decryption(manual_symbols.strip(), pwd_manual)
