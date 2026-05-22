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
# =============================================
# THEME - BLUE HORIZON V2 (Advanced Binary Simulation)
st.set_page_config(page_title="Vari-Crypt: Blue Horizon V2", page_icon="🌐", layout="wide")
import streamlit.components.v1 as _vc

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Roboto+Mono:wght@400;700&display=swap');

@keyframes softPulse{0%{box-shadow:0 0 30px rgba(0,150,255,0.15), inset 0 0 15px rgba(0,100,255,0.1);}50%{box-shadow:0 0 50px rgba(0,150,255,0.35), inset 0 0 30px rgba(0,100,255,0.2);}100%{box-shadow:0 0 30px rgba(0,150,255,0.15), inset 0 0 15px rgba(0,100,255,0.1);}}
@keyframes scanGrad{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}

.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main,[data-testid="stHeader"],[data-testid="stMain"],section.main,.block-container{background:transparent !important; cursor:none !important;}
[data-testid="stAppViewContainer"]>.main{z-index:10;position:relative;}
[data-testid="stHeader"]{backdrop-filter:blur(30px);background:rgba(1,5,15,.7) !important;border-bottom:1px solid rgba(0,150,255,.3);}

html,body,div,p,span,label,li{font-family:'Inter',sans-serif !important;color:#e6f2ff !important;line-height:1.6;font-weight:300;}
h1,h2,h3,h4,h5,h6{font-family:'Inter',sans-serif !important;font-weight:800;letter-spacing:2px;}

h1{text-align:center;margin-bottom:50px;font-size:4rem !important;color:#fff !important;text-shadow:0 0 25px rgba(0,150,255,0.8);letter-spacing:8px;border-bottom:2px solid rgba(0,150,255,0.4);padding-bottom:15px;text-transform:uppercase;}
h2{color:#00aaff !important;font-size:1.6rem !important;letter-spacing:3px;display:inline-block;margin-bottom:25px;text-transform:uppercase;}
h3{color:#fff !important;font-size:1.2rem !important;letter-spacing:2px;font-weight:400;}

code,pre{font-family:'Roboto Mono',monospace !important;color:#00aaff !important;background:rgba(0,150,255,.08);padding:4px 8px;border-radius:4px;border:1px solid rgba(0,150,255,.3);}
section[data-testid="stSidebar"]{background:rgba(1,5,15,.95) !important;backdrop-filter:blur(40px);border-right:1px solid rgba(0,150,255,0.3);box-shadow:10px 0 50px rgba(0,0,0,0.7);}

/* Complex Tech-Glass Panels */
[data-testid="stVerticalBlock"]>div>[data-testid="stVerticalBlock"]{
   background:linear-gradient(135deg, rgba(5,15,40,0.75), rgba(2,5,15,0.9));
   padding:45px;
   backdrop-filter:blur(35px);
   margin-bottom:35px;
   animation:softPulse 6s infinite;
   border: 1px solid rgba(0,150,255,0.3);
   border-radius:20px;
   box-shadow:0 20px 50px rgba(0,0,0,0.8);
   transition:transform 0.4s ease, border-color 0.4s ease;
   position:relative;
}
/* Cyberpunk Corner Accents */
[data-testid="stVerticalBlock"]>div>[data-testid="stVerticalBlock"]::before{
   content:''; position:absolute; top:-1px; left:-1px; width:40px; height:40px;
   border-top:3px solid #00aaff; border-left:3px solid #00aaff; border-top-left-radius:20px;
}
[data-testid="stVerticalBlock"]>div>[data-testid="stVerticalBlock"]::after{
   content:''; position:absolute; bottom:-1px; right:-1px; width:40px; height:40px;
   border-bottom:3px solid #00aaff; border-right:3px solid #00aaff; border-bottom-right-radius:20px;
}
[data-testid="stVerticalBlock"]>div>[data-testid="stVerticalBlock"]:hover{
   transform:translateY(-8px) !important;
   border-color:rgba(0,150,255,0.6);
}

.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]{background:rgba(0,5,15,.7) !important;color:#fff !important;border:1px solid rgba(0,150,255,0.4) !important;border-radius:10px !important;font-family:'Roboto Mono',monospace !important;font-size:1.1rem !important;padding:15px !important;transition:all .3s ease;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#00aaff !important;box-shadow:0 0 20px rgba(0,150,255,.4), inset 0 0 10px rgba(0,150,255,0.2) !important;background:rgba(0,10,30,.9) !important;}
.stTextInput label,.stTextArea label{color:rgba(200,230,255,0.95) !important;font-size:1rem !important;letter-spacing:2px;margin-bottom:10px;font-weight:600;text-transform:uppercase;}

div.stButton>button{width:100%;border:1px solid rgba(0,150,255,0.5);border-radius:12px;padding:16px;background:linear-gradient(270deg, rgba(0,20,50,0.8), rgba(0,80,150,0.6), rgba(0,20,50,0.8));background-size:200% 200%;animation:scanGrad 5s ease infinite;color:#00aaff !important;font-family:'Inter',sans-serif !important;font-weight:800;letter-spacing:3px;font-size:1.2rem !important;transition:all .3s ease;text-transform:uppercase;box-shadow:0 10px 20px rgba(0,0,0,0.5);}
div.stButton>button:hover{background:linear-gradient(270deg, rgba(0,100,255,0.4), rgba(0,150,255,0.6), rgba(0,100,255,0.4));color:#fff !important;box-shadow:0 0 35px rgba(0,150,255,0.5);border-color:#fff;transform:scale(1.02);}

button[data-baseweb="tab"]{background:transparent !important;border:none !important;border-bottom:2px solid transparent !important;color:rgba(255,255,255,0.5) !important;font-family:'Inter',sans-serif !important;font-weight:600;font-size:1.2rem !important;letter-spacing:2px;padding:15px 30px;transition:all .3s ease;text-transform:uppercase;}
button[data-baseweb="tab"][aria-selected="true"]{border-bottom:3px solid #00aaff !important;color:#00aaff !important;text-shadow:0 0 20px rgba(0,150,255,0.6);}
button[data-baseweb="tab"]:hover{color:#fff !important;border-bottom:3px solid rgba(0,150,255,0.5) !important;}

[data-testid="stFileUploader"]{border:2px dashed rgba(0,150,255,0.5);background:rgba(0,150,255,.05);border-radius:16px;padding:50px;transition:all .3s ease;}
[data-testid="stFileUploader"]::before{content:'[ ESTABLISH UPLINK ]';position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:#010512;padding:0 20px;color:#00aaff;font-family:'Roboto Mono',monospace;font-size:.9rem;font-weight:700;letter-spacing:3px;border:1px solid rgba(0,150,255,0.4);border-radius:6px;}
[data-testid="stFileUploader"]:hover{border-color:#00aaff;background:rgba(0,150,255,.1);box-shadow:0 0 40px rgba(0,150,255,.2) inset;transform:translateY(-4px);}

[data-testid="stNotification"],[data-testid="stAlert"]{background:rgba(5,15,35,.98) !important;border:1px solid #00aaff !important;border-left:8px solid #00aaff !important;border-radius:12px !important;box-shadow:0 20px 40px rgba(0,0,0,0.8);padding:20px !important;}
.stProgress>div>div{background:linear-gradient(90deg,#0055ff,#00aaff,#ffffff) !important;border-radius:6px;}
</style>''', unsafe_allow_html=True)
_vc.html("""<!DOCTYPE html><html><body style='margin:0;background:transparent;overflow:hidden;cursor:none;'><script>(function(){
try{
var P=window.parent,D=P.document;
var old=D.getElementById('binaryv2canvas');if(old)old.remove();
var C=D.createElement('canvas');C.id='binaryv2canvas';
C.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-998;pointer-events:none;';
D.body.appendChild(C);
var ctx=C.getContext('2d');
var W,H,dpr,cx,cy;

var cols, rows;
var spacing = 20;
var binaryGrid = [];
var bokeh = [];
var meteors = [];

function init(){
  W=P.innerWidth;H=P.innerHeight;
  dpr=Math.min(P.devicePixelRatio||1, 1.5);
  C.width=W*dpr;C.height=H*dpr;
  ctx.scale(dpr,dpr);
  cx=W/2;cy=H/2;

  cols = Math.ceil(W/spacing);
  rows = Math.ceil(H/spacing);
  binaryGrid = [];

  for(var i=0; i<cols; i++){
     var col = [];
     for(var j=0; j<rows; j++){
        col.push({
           c: Math.random()>0.5 ? '0' : '1',
           offset: Math.random()*Math.PI*2,
           speed: 0.01 + Math.random()*0.02
        });
     }
     binaryGrid.push(col);
  }

  bokeh = [];
  for(var i=0; i<30; i++){
     bokeh.push({
        x: Math.random()*W,
        y: Math.random()*H,
        r: 40 + Math.random()*160,
        vx: (Math.random()-0.5)*0.3,
        vy: (Math.random()-0.5)*0.3,
        alpha: 0.02 + Math.random()*0.1
     });
  }
}

P.addEventListener('resize',init);
init();

var mx=-1000,my=-1000, clickPulse=0;
D.addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY;});
D.addEventListener('mousedown',function(e){clickPulse=1;});

var t=0;

function frame(){
  t++;

  ctx.fillStyle = '#010512';
  ctx.fillRect(0,0,W,H);

  var dynamicBg = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W,H)*0.8);
  dynamicBg.addColorStop(0, 'rgba(0, 80, 220, 0.35)');
  dynamicBg.addColorStop(0.5, 'rgba(0, 20, 100, 0.1)');
  dynamicBg.addColorStop(1, 'transparent');
  ctx.fillStyle = dynamicBg;
  ctx.fillRect(0,0,W,H);

  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<bokeh.length; i++){
     var b = bokeh[i];
     b.x += b.vx; b.y += b.vy;
     if(b.x < -b.r) b.x = W+b.r; if(b.x > W+b.r) b.x = -b.r;
     if(b.y < -b.r) b.y = H+b.r; if(b.y > H+b.r) b.y = -b.r;

     var dx = b.x - mx; var dy = b.y - my;
     var dist = Math.sqrt(dx*dx + dy*dy);
     if(dist < 250){
        b.x += (dx/dist)*2;
        b.y += (dy/dist)*2;
     }

     ctx.beginPath();
     ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
     var bGrad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
     bGrad.addColorStop(0, 'rgba(0, 150, 255, '+(b.alpha)+')');
     bGrad.addColorStop(1, 'rgba(0, 150, 255, 0)');
     ctx.fillStyle = bGrad;
     ctx.fill();
  }
  ctx.globalCompositeOperation = 'source-over';

  // Rotating Central UI Rings
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(t*0.005);
  ctx.beginPath();
  ctx.arc(0, 0, 350, 0, Math.PI*1.5);
  ctx.strokeStyle = 'rgba(0, 150, 255, 0.15)';
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.rotate(-t*0.01);
  ctx.beginPath();
  ctx.arc(0, 0, 370, Math.PI*0.5, Math.PI*2);
  ctx.strokeStyle = 'rgba(0, 200, 255, 0.1)';
  ctx.setLineDash([5, 15]);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();

  // Scanner Beam
  var scanY = (t*5) % (H*2) - H*0.5;
  if(scanY > 0 && scanY < H){
     var scanGrad = ctx.createLinearGradient(0, scanY-50, 0, scanY);
     scanGrad.addColorStop(0, 'transparent');
     scanGrad.addColorStop(1, 'rgba(0, 200, 255, 0.15)');
     ctx.fillStyle = scanGrad;
     ctx.fillRect(0, scanY-50, W, 50);

     ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
     ctx.fillRect(0, scanY, W, 1);
  }

  ctx.font = 'bold 13px "Roboto Mono", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  var connections = [];

  for(var i=0; i<cols; i++){
     for(var j=0; j<rows; j++){
        var cell = binaryGrid[i][j];
        var x = i * spacing + spacing/2;
        var y = j * spacing + spacing/2;

        var wave = Math.sin(x*0.003 + t*0.01) * Math.cos(y*0.003 - t*0.008);
        var individual = Math.sin(t*cell.speed + cell.offset);
        var alpha = (wave + individual) * 0.4 + 0.3;

        var dcx = x - cx; var dcy = y - cy;
        var distCenter = Math.sqrt(dcx*dcx + dcy*dcy);
        var centerFade = Math.max(0, 1 - distCenter/(Math.max(W,H)*0.6));

        alpha *= centerFade;

        var isHighlighted = false;

        var dx = x - mx; var dy = y - my;
        var dist = Math.sqrt(dx*dx + dy*dy);

        if(dist < 150){
           var hoverAlpha = 1 - dist/150;
           alpha = Math.max(alpha, hoverAlpha);
           isHighlighted = true;
           if(Math.random()<0.05) cell.c = cell.c === '0' ? '1' : '0';

           if(dist < 100 && Math.random()<0.2){
              connections.push({x:x, y:y, alpha: hoverAlpha*0.4});
           }
        }

        if(Math.abs(y - scanY) < 30){
           alpha = Math.max(alpha, 1 - Math.abs(y - scanY)/30);
           isHighlighted = true;
           if(Math.random()<0.1) cell.c = cell.c === '0' ? '1' : '0';
        }

        if(clickPulse > 0){
           var waveDist = Math.abs(distCenter - clickPulse*30);
           if(waveDist < 120){
              alpha = Math.max(alpha, 1 - waveDist/120);
              isHighlighted = true;
           }
        }

        if(alpha < 0.05 && clickPulse === 0) continue;
        if(alpha > 1) alpha = 1;

        if(isHighlighted){
           ctx.fillStyle = 'rgba(255, 255, 255, '+(alpha)+')';
        } else {
           ctx.fillStyle = 'rgba(0, 180, 255, '+(alpha*0.8)+')';
        }

        if(Math.random()<0.001) cell.c = cell.c === '0' ? '1' : '0';
        ctx.fillText(cell.c, x, y);
     }
  }

  // Cursor Data Connections (Hacking Effect)
  if(connections.length > 0){
     ctx.beginPath();
     for(var c=0; c<connections.length; c++){
        ctx.moveTo(mx, my);
        ctx.lineTo(connections[c].x, connections[c].y);
     }
     ctx.strokeStyle = 'rgba(0, 200, 255, 0.3)';
     ctx.lineWidth = 0.5;
     ctx.stroke();
  }

  // High-Speed Data Meteors
  if(Math.random()<0.03) {
     meteors.push({
        x: Math.random()*W, y: -50,
        vx: 15, vy: 15,
     });
  }

  for(var i=meteors.length-1; i>=0; i--){
     var m = meteors[i];
     m.x += m.vx; m.y += m.vy;

     var grad = ctx.createLinearGradient(m.x - m.vx*6, m.y - m.vy*6, m.x, m.y);
     grad.addColorStop(0, 'rgba(255,255,255,0)');
     grad.addColorStop(1, 'rgba(0,200,255,0.8)');

     ctx.beginPath();
     ctx.moveTo(m.x - m.vx*6, m.y - m.vy*6);
     ctx.lineTo(m.x, m.y);
     ctx.strokeStyle = grad;
     ctx.lineWidth = 1.5;
     ctx.stroke();

     if(m.x > W+200 || m.y > H+200) meteors.splice(i,1);
  }

  if(clickPulse > 0){
     clickPulse++;
     if(clickPulse > 150) clickPulse = 0;
  }

  var cGrad = ctx.createRadialGradient(mx,my,0, mx,my,150);
  cGrad.addColorStop(0, 'rgba(0, 200, 255, 0.2)');
  cGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = cGrad;
  ctx.fillRect(mx-150, my-150, 300, 300);

  ctx.beginPath();
  ctx.arc(mx, my, 4, 0, Math.PI*2);
  ctx.fillStyle = '#fff';
  ctx.shadowBlur = 10; ctx.shadowColor = '#00aaff';
  ctx.fill(); ctx.shadowBlur = 0;

  requestAnimationFrame(frame);
}
frame();
}catch(e){console.log('binaryv2:',e);}
})();</script></body></html>""", height=0)
st.title("VARI-CRYPT")

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
        st.markdown(f"### 👨🚀 PILOT: `{st.session_state.user_email}`")
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
                            else:
                                st.error("EXTRACTION FAILED. INCORRECT KEY OR DATA CORRUPTION.")
                    except Exception as e:
                        st.error(f"SYSTEM FAILURE: {e}")
