import streamlit as st
import base64
import sqlite3
import hashlib

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT
)
""")
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("bg.jpeg")


# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================================================
# PAGE 1 — LANDING
# ================================================
def render_landing():
    st.set_page_config(layout="wide")
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-position: center;
    }}
    .title {{ font-size: 30px; font-weight: bold; color: white; }}
    div.stButton > button {{
        background-color: rgba(0,0,0,0.3);
        color: white;
        border: 1px solid white;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([7, 2])
    with col1:
        st.markdown('<div class="title">EduVisionAI</div>', unsafe_allow_html=True)
    with col2:
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Login"):
                st.session_state.page = "login"
                st.rerun()
        with b2:
            if st.button("Sign Up"):
                st.session_state.page = "login"
                st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style='text-align:center; color:white;'>
            <div style='font-size:40px; font-weight:800;'>Learning Faces, Smarter Classes</div>
            <div style='font-size:32px; font-weight:700; margin-top:10px;'>Turning Expressions into Insights.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:white;'>Explore Features</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("1i.png", use_container_width=True)
    with col2:
        st.image("2i.png", use_container_width=True)
    with col3:
        st.image("3i.png", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    .about-wrap { padding: 20px 0 60px; text-align: center; }
    .about-label { font-size: 44px; font-weight: 700; letter-spacing: 3px; color: teal; text-transform: uppercase; margin-bottom: 10px; }
    .about-heading { font-size: 22px; font-weight: 800; color: white; margin-bottom: 36px; }
    .about-card-title { font-size: 32px; font-weight: 800; color: white; line-height: 1.35; margin-bottom: 20px; }
    .about-text { font-size: 20px !important; color: #94a3b8; line-height: 1.8; margin-bottom: 14px; }
    .about-text strong { color: white; font-weight: 700; }
    </style>
    <div class="about-wrap">
        <div class="about-label">About the Project</div>
        <div class="about-heading">Why We Built This</div>
        <div class="about-card-title">Turning Expressions into <span>Insights</span></div>
        <p class="about-text">EduVisionAI is a team project built with a simple but powerful belief —
        <strong>every student's face tells a story</strong>, and teachers deserve to hear it in real time.</p>
        <p class="about-text">We combined computer vision, facial recognition, and emotion AI to create a platform
        that makes classrooms smarter — automating attendance and illuminating what really matters: are students actually learning?</p>
        <p class="about-text">Our goal is to give educators the data they need to teach better, respond faster, and
        connect more deeply with every student in the room.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .hiw-wrap { padding: 20px 0 80px; text-align: center; }
    .hiw-label { font-size: 44px; font-weight: 700; letter-spacing: 3px; color: #2dd4bf; text-transform: uppercase; margin-bottom: 10px; }
    .hiw-heading { font-size: 22px; font-weight: 800; color: white; margin-bottom: 8px; }
    .hiw-sub { font-size: 15px; color: #94a3b8; margin-bottom: 48px; }
    .hiw-grid { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; max-width: 1050px; margin: 0 auto; }
    .hiw-card { background: rgba(10,35,45,0.85); border: 1px solid rgba(45,212,191,0.2); border-radius: 18px; padding: 42px 28px 38px; width: 290px; text-align: center; }
    .hiw-num { width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #2dd4bf); color: white; font-size: 22px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
    .hiw-card-title { font-size: 18px; font-weight: 700; color: white; margin-bottom: 12px; }
    .hiw-card-body { font-size: 14px; color: #94a3b8; line-height: 1.75; }
    </style>
    <div class="hiw-wrap">
        <div class="hiw-label">The Process</div>
        <div class="hiw-heading">How It Works</div>
        <div class="hiw-sub">Three simple steps. Powerful results.</div>
        <div class="hiw-grid">
            <div class="hiw-card"><div class="hiw-num">1</div><div class="hiw-card-title">Camera Captures</div><div class="hiw-card-body">The system uses the classroom camera to detect and identify each student's face as class begins.</div></div>
            <div class="hiw-card"><div class="hiw-num">2</div><div class="hiw-card-title">AI Analyzes</div><div class="hiw-card-body">Our AI model reads facial expressions in real time — tracking engagement, confusion, distraction, and more.</div></div>
            <div class="hiw-card"><div class="hiw-num">3</div><div class="hiw-card-title">Teacher Sees</div><div class="hiw-card-body">Teachers get a live dashboard with attendance, emotion charts, and class-wide engagement scores — instantly.</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .footer-wrap {
        background: rgba(0, 10, 15, 0.75);
        border-top: 2px solid rgba(45, 212, 191, 0.3);
        padding: 50px 40px 25px;
        margin-top: 40px;
    }
    .footer-grid { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 36px; margin-bottom: 40px; }
    .footer-brand-title { font-size: 20px; font-weight: 800; color: #2dd4bf; margin-bottom: 8px; }
    .footer-brand-desc { font-size: 13px; color: #94a3b8; max-width: 200px; line-height: 1.7; }
    .social-row { display: flex; gap: 10px; margin-top: 16px; }
    .social-icon { width: 34px; height: 34px; border-radius: 50%; border: 1px solid rgba(45,212,191,0.35); display: inline-flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 13px; text-decoration: none; }
    .footer-col-title { font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #2dd4bf; margin-bottom: 14px; }
    .footer-col a { display: block; font-size: 13px; color: #94a3b8; text-decoration: none; margin-bottom: 9px; }
    .founders-row { display: flex; gap: 14px; flex-wrap: wrap; }
    .founder-card { text-align: center; }
    .founder-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #2dd4bf); display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800; color: white; margin: 0 auto 5px; border: 2px solid rgba(45,212,191,0.4); }
    .founder-name { font-size: 10px; color: #94a3b8; white-space: nowrap; }
    .footer-divider { border: none; border-top: 1px solid rgba(45,212,191,0.15); margin: 0 0 18px; }
    .footer-bottom { text-align: center; font-size: 12px; color: #475569; }
    </style>
    <div class="footer-wrap">
        <div class="footer-grid">
            <div>
                <div class="footer-brand-title">EduVisionAI</div>
                <div class="footer-brand-desc">Learning Faces, Smarter Classes. Turning expressions into real-time insights for educators.</div>
                <div class="social-row">
                    <a class="social-icon" href="#">in</a>
                    <a class="social-icon" href="#">X</a>
                    <a class="social-icon" href="#">yt</a>
                    <a class="social-icon" href="#">ig</a>
                </div>
            </div>
            <div class="footer-col">
                <div class="footer-col-title">About</div>
                <a href="#">Our Mission</a>
                <a href="#">How It Works</a>
                <a href="#">Why EduVision</a>
                <a href="#">Blog</a>
            </div>
            <div class="footer-col">
                <div class="footer-col-title">Support</div>
                <a href="#">Help Center</a>
                <a href="#">Documentation</a>
                <a href="#">FAQs</a>
                <a href="#">Privacy Policy</a>
            </div>
            <div class="footer-col">
                <div class="footer-col-title">Contact Us</div>
                <a href="#">eduvisionai@gmail.com</a>
                <a href="#">Partner With Us</a>
                <a href="#">Request a Demo</a>
            </div>
            <div>
                <div class="footer-col-title">Founders</div>
                <div class="founders-row">
                    <div class="founder-card">
                        <div class="founder-avatar">T</div>
                        <div class="founder-name">Tia Sharma</div>
                    </div>
                    <div class="founder-card">
                        <div class="founder-avatar">M</div>
                        <div class="founder-name">Manya Sharma</div>
                    </div>
                    <div class="founder-card">
                        <div class="founder-avatar">V</div>
                        <div class="founder-name">Vaibhavi Sethi</div>
                    </div>
                    <div class="founder-card">
                        <div class="founder-avatar">P</div>
                        <div class="founder-name">Pushpita</div>
                    </div>
                </div>
            </div>
        </div>
        <hr class="footer-divider">
        <div class="footer-bottom">@2026 EduVisionAI. All rights reserved.</div>
    </div>
    """, unsafe_allow_html=True)


# ================================================
# PAGE 2 — LOGIN / SIGNUP
# ================================================
def render_login():
    st.set_page_config(page_title='EduVisionAi', layout='centered')
    st.markdown(f"""
    <style>
    .stApp {{ background-image: url("data:image/jpeg;base64,{img}"); background-size: cover; background-position: center; }}
    .block-container {{ padding-top: 8vh; }}
    .login-card {{ background-color: rgba(0,0,0,0.55); padding: 2.5rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px); }}
    .title {{ font-size: 32px; font-weight: bold; color: white; text-align: center; }}
    .subtitle {{ font-size: 14px; color: rgba(255,255,255,0.7); text-align: center; margin-bottom: 20px; }}
    label {{ color: white !important; }}
    div.stButton > button {{ width: 100%; background-color: rgba(255,255,255,0.15); color: white; border-radius: 8px; }}
    div.stButton > button:hover {{ background-color: rgba(255,255,255,0.3); }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">EduVisionAi</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Analytics Dashboard</div>', unsafe_allow_html=True)

        menu = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")

        if menu == "Login":
            st.subheader("Login")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login"):
                if login_user and login_pass:
                    hashed_pw = hash_password(login_pass)
                    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (login_user, hashed_pw))
                    user = cursor.fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.session_state.page = "meet"
                        st.rerun()
                    else:
                        st.error("Invalid username or password ❌")
                else:
                    st.warning("Please fill all fields ⚠️")

        elif menu == "Sign Up":
            st.subheader("Create Account")
            signup_user = st.text_input("Username", key="signup_user")
            signup_email = st.text_input("Email", key="signup_email")
            signup_pass = st.text_input("Password", type="password", key="signup_pass")

            if st.button("Sign Up"):
                if signup_user and signup_email and signup_pass:
                    try:
                        hashed_pw = hash_password(signup_pass)
                        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (signup_user, signup_email, hashed_pw))
                        conn.commit()
                        st.success("Account created! Please login 🎉")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists ❌")
                else:
                    st.warning("Please fill all fields ⚠️")

        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.caption("© 2026 EduVisionAi. All rights reserved.")


# ================================================
# PAGE 3 — MEET
# ================================================
def render_meet():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    st.set_page_config(page_title="AI Smart Classroom", page_icon="A", layout="wide")
    st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 30% 25%, #0b6a6e 0%, #04565c 42%, #02464c 100%); color: #e2e8f0; }
    .main-card { max-width: 900px; margin: 1.5rem auto; padding: 2rem; border-radius: 18px; background: rgba(15,23,42,0.75); border: 1px solid rgba(148,163,184,0.25); box-shadow: 0 20px 45px rgba(2,6,23,0.45); backdrop-filter: blur(6px); }
    .hero-title { font-size: 2.4rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.7rem; color: #f8fafc; }
    .hero-sub { color: #cbd5e1; font-size: 1.02rem; margin-bottom: 1.3rem; }
    .feature { background: rgba(30,41,59,0.55); border: 1px solid rgba(100,116,139,0.25); border-radius: 12px; padding: 0.9rem; margin-bottom: 0.8rem; color: #e2e8f0; }
    .footer-note { margin-top: 1rem; color: #94a3b8; font-size: 0.9rem; }
    div.stButton > button { border-radius: 10px !important; border: 1px solid rgba(56,189,248,0.45) !important; padding: 0.58rem 1.05rem !important; font-weight: 600 !important; }
    .page-title { font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem; }
    .page-sub { color: #cbd5e1; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

    class_link = "https://meet.google.com/your-class-link"

    if "meet_page" not in st.session_state:
        st.session_state.meet_page = "home"

    def go_to(p):
        st.session_state.meet_page = p

    if st.session_state.meet_page == "join":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">Join a Meeting</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Enter your details and click continue to open the meeting room.</div>', unsafe_allow_html=True)
        name = st.text_input("Your Name", placeholder="Enter your name")
        meeting_code = st.text_input("Meeting Code", placeholder="Enter class/meeting code")
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("Continue to Meeting", class_link, use_container_width=True)
        with col2:
            if st.button("Back to Home", use_container_width=True):
                go_to("home"); st.rerun()
        if name or meeting_code:
            st.info(f"Ready to join as: {name or 'Guest'} | Code: {meeting_code or 'Not entered'}")
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.meet_page == "host":
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="page-title">Host a Meeting</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Create your session details and start hosting your class.</div>', unsafe_allow_html=True)
        host_name = st.text_input("Host Name", placeholder="Enter host name")
        topic = st.text_input("Meeting Topic", placeholder="e.g. AI Basics - Session 1")
        duration = st.selectbox("Duration", ["30 mins", "45 mins", "60 mins", "90 mins"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Hosting", use_container_width=True):
                st.success(f"Meeting ready! Host: {host_name or 'Teacher'} | Topic: {topic or 'Classroom Session'} | Duration: {duration}")
        with col2:
            if st.button("Back to Home", use_container_width=True):
                go_to("home"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">EduVisionAi</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Join your live class with one click and keep learning organized, interactive, and future-ready.</div>', unsafe_allow_html=True)
        left, right = st.columns([1.2, 1], gap="large")
        with left:
            if st.button("Join a Meeting", use_container_width=True):
                go_to("join"); st.rerun()
            if st.button("Host a Meeting", use_container_width=True):
                go_to("host"); st.rerun()
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.page = "landing"
                st.rerun()
            st.markdown('<p class="footer-note">Need help? Contact your class coordinator.</p>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="feature">Structured lessons and quick access resources.</div>', unsafe_allow_html=True)
            st.markdown('<div class="feature">AI-assisted classroom engagement tools.</div>', unsafe_allow_html=True)
            st.markdown('<div class="feature">Stay updated with live session reminders.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ================================================
# ROUTER
# ================================================
if st.session_state.page == "login":
    render_login()
elif st.session_state.page == "meet":
    render_meet()
else:
    render_landing()