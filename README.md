# vari-crypt-app
# 🔐 Vari-Crypt: Secure Visual Messaging System

[cite_start]**Vari-Crypt** is a secure, lightweight communication tool that combines industrial-grade AES-256 (EAX Mode) encryption with a Visual Mapping Layer[cite: 16]. [cite_start]It transforms short messages (up to 20 words) into a visually noisy string of emojis, mathematical symbols, Greek letters, and alphanumeric characters, making secure communication appear as random digital artifacts[cite: 17].

**Academic Context:**
* [cite_start]**Course:** Bachelor of Computer Application [cite: 11]
* [cite_start]**Institution:** Bengaluru City University [cite: 12]
* [cite_start]**Submitted By:** RAJKUMAR B (USN: U18UZ23S0134) [cite: 6, 7]
* [cite_start]**Guide:** Prof. Harish [cite: 9]

---

## 🎯 Problem Statement & Aim
[cite_start]Standard encrypted data is easily identifiable as ciphertext, which can attract unwanted attention from interceptors[cite: 19]. [cite_start]There is a need for a lightweight tool that not only secures short-form text but also masks it behind a password-shuffled visual language to provide an additional layer of security through obscurity[cite: 21].

[cite_start]**Project Aim:** To design and develop a Python-based application that encrypts and transforms short text data into a multi-domain symbol language using custom and password-seeded random mapping[cite: 23].

---

## ✨ Key Features & Objectives
* [cite_start]**Implement Secure Encryption:** Uses AES-256 in EAX mode for authenticated encryption to ensure data integrity[cite: 25].
* [cite_start]**Develop Mapping Engine:** Utilizes a Symbol Universe of 256 unique characters across Emoji, Math, English, Greek, and Alphanumeric domains[cite: 26].
* [cite_start]**Dual-Mode Sharing:** Supports sharing via Cloud (MongoDB Database) or Manual Standalone Paste (Offline)[cite: 27].
* [cite_start]**Constraint Management:** Enforces a strict 0–20 word limit for optimized real-time processing[cite: 28].
* [cite_start]**Real-Time UI:** Integrates the logic into a real-time Streamlit dashboard for instant transformation[cite: 29].

---

## 🛠️ Tools and Technologies Used
* [cite_start]**Programming Language:** Python [cite: 46]
* [cite_start]**Security Libraries:** PyCryptodome (AES-256), Argon2-cffi (Key Derivation) [cite: 47]
* [cite_start]**Frontend Framework:** Streamlit [cite: 49]
* **Backend Framework:** FastAPI & Uvicorn
* **Cloud Database:** MongoDB Atlas (NoSQL)

---

## ⚙️ Working Structure of the System
1.  [cite_start]**Input:** User enters the text (max 20 words) and a secret key/password[cite: 31].
2.  [cite_start]**Key Derivation:** The system derives a 32-byte key using Argon2[cite: 32].
3.  [cite_start]**Encryption:** The message is encrypted into binary ciphertext using AES-256-EAX[cite: 33].
4.  [cite_start]**Mapping Engine:** Shuffles the 256-symbol pool deterministically based on the password seed[cite: 34].
5.  [cite_start]**Obfuscation:** Each byte of the encrypted package is replaced with its corresponding symbol from the pool[cite: 35].
6.  **Transmission:** The visual payload is either stored in MongoDB or copied manually by the user.
7.  [cite_start]**Decryption:** The receiver reverses these steps (Symbol → Byte → Decryption) using the same password to retrieve the original text[cite: 36].

---

## 🚀 How to Run Locally

### Prerequisites
Ensure you have Python 3.8+ installed. 

### 1. Install Dependencies
```bash
pip install -r requirements.txt
