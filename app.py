import streamlit as st
import streamlit_option_menu
import database
import camera_detection
import time

# SESSION STATE INIT 
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'redirect_to' not in st.session_state:
    st.session_state.redirect_to = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'detector' not in st.session_state:
    st.session_state.detector = None
# timestamp used to optionally auto‑stop the camera after a period
if 'camera_start_time' not in st.session_state:
    st.session_state.camera_start_time = None
if 'age' not in st.session_state:
    st.session_state.age = None
if 'avatar' not in st.session_state:
    st.session_state.avatar = None
if 'show_profile_upload' not in st.session_state:
    st.session_state.show_profile_upload = False

#PAGE CONFIG
st.set_page_config(
    page_title="EmoRecs | Emotion-Based Recommendation System",
    page_icon="😊",
    layout="wide"
)

# CUSTOM CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #5c6bc0 0%, #7986cb 100%);
    color: #ffffff !important;
}

[data-testid="stApp"] {
    background: linear-gradient(180deg, #5c6bc0 0%, #7986cb 100%) !important;
    color: #ffffff !important;
}

/* Header Styles */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 8%;
    background: rgba(26, 35, 126, 0.98);
    border-bottom: 1px solid rgba(108, 99, 255, 0.3);
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 700;
    font-size: 1.2rem;
    color: #ffffff !important;
}

.logo svg {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6c63ff, #00d2ff);
    padding: 6px;
}

nav a {
    margin-left: 28px;
    text-decoration: none;
    color: #ffffff !important;
    opacity: 0.85;
    font-weight: 400;
}

nav a:hover {
    opacity: 1;
    color: #00d2ff !important;
}

/* Hero Section */
.hero {
    padding: 80px 8% 120px;
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
}

.hero h1 {
    font-size: 3rem;
    line-height: 1.2;
    margin-bottom: 20px;
    color: #1a1a2e !important;
}

.hero p {
    font-size: 1.05rem;
    opacity: 0.9;
    max-width: 520px;
    margin-bottom: 32px;
    color: #495057 !important;
}

/* Buttons */
.btn-primary {
    background: linear-gradient(135deg, #6c63ff, #00d2ff);
    color: #fff;
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    box-shadow: 0 10px 30px rgba(108, 99, 255, 0.35);
    cursor: pointer;
    transition: 0.3s;
}

.btn-primary:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 30px rgba(108, 99, 255, 0.6);
}

.btn-outline {
    background: transparent;
    color: #1a1a2e;
    border: 1px solid rgba(26, 26, 46, 0.3);
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.3s;
}

.btn-outline:hover {
    border-color: #6c63ff;
    color: #6c63ff;
}

/* Visual Section */
.visual {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15);
}

.visual h3 {
    margin-bottom: 16px;
    font-weight: 600;
    color: #1a1a2e !important;
}

.emotion-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}

.emotion {
    padding: 18px 12px;
    border-radius: 16px;
    background: rgba(108, 99, 255, 0.1);
    text-align: center;
    font-size: 0.9rem;
    color: #1a1a2e !important;
}

/* Features */
.features-section {
    padding: 80px 8%;
}

.features-section h2 {
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: 48px;
    color: #f5f7ff !important;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 28px;
}

.card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 28px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.card h3, .card h4 {
    margin-bottom: 12px;
    font-weight: 600;
    color: #f5f7ff !important;
}

.card p {
    opacity: 0.9;
    font-size: 0.95rem;
    color: #e0e0e0 !important;
}

/* How It Works */
.how-section {
    padding: 80px 8% 100px;
}

.how-section h2 {
    text-align: center;
    margin-bottom: 40px;
    font-size: 2.2rem;
    color: #f5f7ff !important;
}

.steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 28px;
}

.step {
    padding: 24px;
    border-left: 4px solid #6c63ff;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 12px;
}

.step h4 {
    margin-bottom: 8px;
    color: #f5f7ff !important;
}

.step p {
    opacity: 0.9;
    font-size: 0.95rem;
    color: #e0e0e0 !important;
}

/* Footer */
footer {
    padding: 40px 8%;
    text-align: center;
    opacity: 0.7;
    font-size: 0.9rem;
    color: #cccccc !important;
}

/* Auth Section */
.auth-section {
    padding: 80px 8%;
    padding-top: 40px;
}

.auth-section h2 {
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: 20px;
    color: #f5f7ff !important;
}

.auth-section > p {
    text-align: center;
    max-width: 600px;
    margin: 0 auto 40px;
    opacity: 0.9;
    color: #e0e0e0 !important;
}

.auth-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 28px;
    max-width: 800px;
    margin: 0 auto;
}

.signup-card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 28px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.signup-card h3 {
    margin-bottom: 12px;
    font-weight: 600;
    color: #f5f7ff !important;
}

.signup-card > p {
    opacity: 0.9;
    font-size: 0.95rem;
    margin-bottom: 20px;
    color: #e0e0e0 !important;
}

.form-input {
    width: 100%;
    padding: 12px;
    border-radius: 12px;
    border: none;
    margin-bottom: 12px;
    font-family: 'Poppins', sans-serif;
}

.form-input:focus {
    outline: 2px solid #6c63ff;
}

.form-input:last-of-type {
    margin-bottom: 16px;
}

.terms {
    margin-top: 12px;
    font-size: 0.85rem;
    opacity: 0.8;
    color: #cccccc !important;
}

.terms a {
    color: #9aa0ff !important;
}

/* Auth, Dashboard, Admin Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ffa500) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-family: 'Poppins', sans-serif !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff5252, #ff9800) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6) !important;
}

/* Responsive */
@media (max-width: 900px) {
    .hero {
        grid-template-columns: 1fr;
        padding-top: 40px;
    }
    
    .hero h1 {
        font-size: 2.3rem;
    }
}

/* Admin Users Table Styling */
.admin-users-section {
    background: linear-gradient(135deg, #1e1e2f 0%, #2d1b4e 50%, #1a1a3e 100%);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), 0 0 60px rgba(108, 99, 255, 0.15);
    border: 1px solid rgba(108, 99, 255, 0.3);
    margin-top: 20px;
}

.admin-users-section h3 {
    color: #ffffff !important;
    font-weight: 600;
    margin-bottom: 16px;
    font-size: 1.3rem;
    text-shadow: 0 2px 10px rgba(108, 99, 255, 0.5);
}

.admin-users-section .stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* DataFrame Custom Styling */
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
}

/* Table Header */
[data-testid="stDataFrame"] thead th {
    background: linear-gradient(135deg, #6c63ff, #00d2ff) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 14px !important;
    border-bottom: 2px solid rgba(255, 255, 255, 0.2) !important;
}

/* Table Body */
[data-testid="stDataFrame"] tbody td {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #e0e0e0 !important;
    padding: 12px 14px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Table Row Hover */
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(108, 99, 255, 0.2) !important;
    color: #ffffff !important;
}

/* Alternate Row Colors */
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: rgba(255, 255, 255, 0.04) !important;
}

/* Tab Container Styling */
.users-tab-content {
    background: linear-gradient(135deg, #232136 0%, #2a2045 100%);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Stats Cards Enhancement */
.stats-card {
    background: linear-gradient(135deg, #2d1b4e, #1e1e2f) !important;
    border: 1px solid rgba(108, 99, 255, 0.4) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
}

.stats-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(108, 99, 255, 0.3) !important;
    transition: all 0.3s ease;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e0c3fc 0%, #8ec5fc 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #1a1a2e !important;
}

/* Sidebar Radio Button - Remove Red Color on Selection */
div[data-testid="stRadio"] > div {
    background: transparent !important;
}

div[data-testid="stRadio"] label {
    color: #1a1a2e !important;
}

div[data-testid="stRadio"] .stRadio > div[role="radiogroup"] > label {
    background: transparent !important;
    color: #1a1a2e !important;
}

div[data-testid="stRadio"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
    background: transparent !important;
    color: #1a1a2e !important;
}

div[data-testid="stRadio"] .stRadio > div[role="radiogroup"] > label:has(input:checked)::before {
    background: transparent !important;
    box-shadow: none !important;
}

/* Ensure native radio accent isn't showing red */
div[data-testid="stRadio"] input[type="radio"] {
    accent-color: transparent !important;
}

/* Alert Messages Styling for Visibility */
.stAlert-success {
    background: rgba(76, 175, 80, 0.9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(76, 175, 80, 0.5) !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-weight: 500 !important;
}

.stAlert-error {
    background: rgba(244, 67, 54, 0.9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(244, 67, 54, 0.5) !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-weight: 500 !important;
}

.stAlert-warning {
    background: rgba(255, 152, 0, 0.9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 152, 0, 0.5) !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-weight: 500 !important;
}

.stAlert-info {
    background: rgba(33, 150, 243, 0.9) !important;
    color: #ffffff !important;
    border: 1px solid rgba(33, 150, 243, 0.5) !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# HEADER 
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding: 24px 8%; background: rgba(11, 14, 43, 0.95); border-bottom: 1px solid rgba(108, 99, 255, 0.3);">
    <div style="display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 1.2rem; color: #f5f7ff;">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="white" stroke-width="2"/>
            <path d="M8 14c1.2 1 2.5 1.5 4 1.5s2.8-.5 4-1.5" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <circle cx="9" cy="10" r="1" fill="white"/>
            <circle cx="15" cy="10" r="1" fill="white"/>
        </svg>
        EmoRecs
    </div>
</div>
""", unsafe_allow_html=True)

#  SIDEBAR NAVIGATION
if st.session_state.logged_in:
    sidebar_options = ["Home", "Features", "How It Works", "Detect Emotion", "Dashboard", "Admin"]
else:
    sidebar_options = ["Home", "Features", "How It Works", "Auth"]

# Reset sidebar_selected if not in current options (e.g., after login/logout)
if 'sidebar_selected' not in st.session_state or st.session_state.sidebar_selected not in sidebar_options:
    st.session_state.sidebar_selected = sidebar_options[0]

# SIDEBAR PROFILE SECTION - ALWAYS VISIBLE (logged-in or not)
st.sidebar.markdown(
    """
    <style>
    .profile-section { margin: 0 !important; padding: 5px 0 !important; }
    .profile-title { margin: 0 !important; padding: 0 !important; }
    button[key="profile_upload_btn"] { padding: 2px 4px !important; font-size: 10px !important; height: 28px !important; }
    </style>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("### 👤 Profile", unsafe_allow_html=True)

if st.session_state.logged_in:
    # Profile card - image with + icon attached
    col_img, col_btn = st.sidebar.columns([3, 0.8], gap="small")
    
    with col_img:
        if st.session_state.avatar:
            try:
                st.image(st.session_state.avatar, width=60)
            except Exception:
                st.image("https://i.pravatar.cc/200?u=" + (st.session_state.username or "user"), width=60)
        else:
            st.image("https://i.pravatar.cc/200?u=" + (st.session_state.username or "user"), width=60)
    
    with col_btn:
        st.write("")
        if st.button("➕", key="profile_upload_btn", help="Upload"):
            st.session_state.show_profile_upload = not st.session_state.show_profile_upload
    
    # File uploader appears when + clicked
    if st.session_state.get("show_profile_upload", False):
        uploaded_image = st.sidebar.file_uploader("Select image", type=["jpg", "jpeg", "png"], key="profile_pic_upload", label_visibility="collapsed")
        
        if uploaded_image is not None:
            # Read and save the image
            import base64
            image_bytes = uploaded_image.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_data_uri = f"data:image/{uploaded_image.type};base64,{image_base64}"
            
            st.session_state.avatar = image_data_uri
            st.session_state.show_profile_upload = False
            # Update in database
            success, message = database.update_user_profile(st.session_state.user_id, avatar=image_data_uri)
            if success:
                st.success("Photo updated!")
                st.rerun()
            else:
                st.error(message)
    
    # User details (compact)
    st.sidebar.markdown(f"<p style='margin: 0; padding: 0; font-size: 0.9rem;'><b>{st.session_state.username or 'User'}</b></p>", unsafe_allow_html=True)
    if st.session_state.age:
        st.sidebar.markdown(f"<p style='margin: 0; padding: 0; font-size: 0.8rem;'>Age: {st.session_state.age}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='margin: 0; padding: 0; font-size: 0.8rem;'>Email: {(st.session_state.email or 'N/A')}</p>", unsafe_allow_html=True)
    
    # Expandable profile details for age editing
    with st.sidebar.expander("Edit Profile"):
        new_age = st.number_input(
            "Age", 
            min_value=0, 
            max_value=120, 
            value=(st.session_state.age if st.session_state.age else 25),
            key="sidebar_age_edit"
        )
        
        if st.button("Save Age", key="save_age_btn"):
            st.session_state.age = new_age
            # Update in database
            success, message = database.update_user_profile(st.session_state.user_id, age=new_age)
            if success:
                st.success("Age updated!")
            else:
                st.error(message)
else:
    # Not logged in - show plain profile tab with no image
    st.sidebar.markdown("<p style='margin: 0; padding: 10px 0; font-size: 0.8rem; text-align: center; color: #999;'>Login to view profile</p>", unsafe_allow_html=True)

    
    st.sidebar.divider()

# Sidebar navigation
st.sidebar.title(" Navigation")
sidebar_selection = st.sidebar.selectbox("Go to:", sidebar_options, index=sidebar_options.index(st.session_state.sidebar_selected))

if sidebar_selection != st.session_state.sidebar_selected:
    st.session_state.sidebar_selected = sidebar_selection
    st.rerun()

# MAIN NAVIGATION
if st.session_state.logged_in:
    menu_options = ["Home", "Features", "How It Works", "Detect Emotion", "Dashboard", "Admin"]
    menu_icons = ["house", "stars", "diagram-3", "camera", "person-circle", "shield-check"]
else:
    menu_options = ["Home", "Features", "How It Works", "Auth"]
    menu_icons = ["house", "stars", "diagram-3", "person-circle"]

default_idx = menu_options.index(st.session_state.sidebar_selected) if st.session_state.sidebar_selected in menu_options else 0

# Handle redirect after login
if st.session_state.redirect_to == "Auth":
    st.session_state.redirect_to = None
    st.session_state.sidebar_selected = "Auth"
    default_idx = menu_options.index("Auth") if "Auth" in menu_options else 0
elif st.session_state.redirect_to == "Detect Emotion":
    st.session_state.redirect_to = None
    st.session_state.sidebar_selected = "Detect Emotion"
    default_idx = menu_options.index("Detect Emotion") if "Detect Emotion" in menu_options else 0

selected = streamlit_option_menu.option_menu(
    menu_title=None,
    options=menu_options,
    icons=menu_icons,
    orientation="horizontal",
    default_index=default_idx,
    styles={
        "container": {"padding": "0"},
        "nav-link": {"color": "#F0540BFF", "opacity": "0.85"},
        "nav-link-selected": {"background": "linear-gradient(135deg, #6c63ff, #00d2ff)", "opacity": "1"},
    }
)

# Sync sidebar with main navigation
if selected != st.session_state.sidebar_selected:
    st.session_state.sidebar_selected = selected

# HOME
if selected == "Home":
    st.markdown("""
    <div style="padding: 80px 8% 120px; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 48px; align-items: center;">
        <div>
            <h1 style="font-size: 3rem; line-height: 1.2; margin-bottom: 20px; color: #f5f7ff;">Emotion-Based<br>Smart Recommendations</h1>
            <p style="font-size: 1.05rem; opacity: 0.9; max-width: 520px; margin-bottom: 32px; color: #e0e0e0;">
                EmoRecs detects your real-time facial emotions using AI and computer vision,
                then recommends movies, music, games, and books that truly match how you feel.
            </p>
        </div>
        <div class="visual">
            <h3>Detectable  Emotions</h3>
            <div class="emotion-grid">
                <div class="emotion">😊 Happy</div>
                <div class="emotion">😌 Calm</div>
                <div class="emotion">😢 Sad</div>
                <div class="emotion">😠 Angry</div>
                <div class="emotion">😲 Surprised</div>
                <div class="emotion">😐 Neutral</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# FEATURES 
elif selected == "Features":
    st.markdown("""
    <div class="features-section" id="features">
        <h2>Powerful Features</h2>
        <div class="feature-grid">
            <div class="card">
                <h3>🎥 Real-Time Emotion Detection</h3>
                <p>Uses computer vision and OpenCV to analyze facial expressions instantly.</p>
            </div>
            <div class="card">
                <h4>🤖 AI-Driven Recommendations</h4>
                <p>Smart ML models suggest content that matches your current mood.</p>
            </div>
            <div class="card">
                <h3>🌐 Internet-Wide Content</h3>
                <p>Fetches movies, music, games, and books using real-time APIs.</p>
            </div>
            <div class="card">
                <h3>⚡ Streamlit Powered</h3>
                <p>Fast, interactive, and modern web interface built with Streamlit.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# HOW IT WORKS 
elif selected == "How It Works":
    st.markdown("""
    <div class="how-section" id="how">
        <h2>How It Works</h2>
        <div class="steps">
            <div class="step">
                <h4>1. Capture Emotion</h4>
                <p>Your webcam captures facial expressions in real time.</p>
            </div>
            <div class="step">
                <h4>2. Analyze Emotions through Face</h4>
                <p>AI models classify emotions using trained datasets.</p>
            </div>
            <div class="step">
                <h4>3. Recommend Content</h4>
                <p>Relevant movies, music, games, and books are suggested instantly.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# DETECT EMOTION 
elif selected == "Detect Emotion":
    st.markdown("""
    <div class="auth-section">
        <h2>📸 Detect Your Emotion</h2>
        <p>Use your camera to detect your current emotional state</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Camera controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3> Camera Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Start/Stop camera button
        if not st.session_state.camera_active:
            if st.button("📷 Start Camera", key="start_camera"):
                # Initialize camera
                detector = camera_detection.CameraDetector()
                success, message = detector.initialize()
                if success:
                    st.session_state.detector = detector
                    st.session_state.camera_active = True
                    st.session_state.camera_start_time = time.time()
                    st.rerun()
                else:
                    st.error(message)
        else:
            if st.button("⏹ Stop Camera", key="stop_camera"):
                if st.session_state.detector:
                    st.session_state.detector.release()
                st.session_state.detector = None
                st.session_state.camera_active = False
                st.session_state.camera_start_time = None
                st.rerun()
        
        # Camera info
        st.markdown("""
        <div class="card" style="margin-top: 20px;">
            <h4> Instructions</h4>
            <p>1. Click "Start Camera" to begin</p>
            <p>2. Allow camera access when prompted</p>
            <p>3. Position your face in the frame</p>
            <p>4. The system will detect your emotion</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.camera_active and st.session_state.detector:
            # Create placeholders for updating content without full reruns
            frame_placeholder = st.empty()
            info_placeholder = st.empty()
            emotion_col1, emotion_col2, emotion_col3 = st.columns(3)
            emotion_display_col1 = emotion_col1.empty()
            emotion_display_col2 = emotion_col2.empty()
            emotion_display_col3 = emotion_col3.empty()
            
            # Track detected emotions
            emotions_detected = []
            start_time = time.time()
            frame_count = 0
            
            # Smooth camera loop - capture frames continuously
            while st.session_state.camera_active:
                try:
                    success, frame = st.session_state.detector.get_frame()
                    if success and frame is not None:
                        # Process frame for face and emotion detection
                        processed_frame, face_data = st.session_state.detector.process_frame(frame)
                        img = camera_detection.convert_frame_to_image(processed_frame)
                        
                        # Update frame display
                        frame_placeholder.image(img, caption="Live Camera Feed - Emotion Detection", use_container_width=True)
                        
                        # Update face/emotion info
                        if len(face_data) > 0:
                            info_placeholder.success(f"✓ Detected {len(face_data)} face(s)")
                            
                            # Display emotions for detected faces
                            emotions_detected = []
                            for i, (x, y, w, h, emotion, confidence) in enumerate(face_data):
                                emotions_detected.append({
                                    'emotion': emotion,
                                    'confidence': confidence
                                })
                                
                                if i == 0:
                                    emotion_display_col1.metric(f"Face {i+1} Emotion", emotion, f"{confidence:.1%}")
                                elif i == 1:
                                    emotion_display_col2.metric(f"Face {i+1} Emotion", emotion, f"{confidence:.1%}")
                                elif i == 2:
                                    emotion_display_col3.metric(f"Face {i+1} Emotion", emotion, f"{confidence:.1%}")
                        else:
                            info_placeholder.warning("⚠ No face detected. Position your face in the frame.")
                            emotion_display_col1.empty()
                            emotion_display_col2.empty()
                            emotion_display_col3.empty()
                    else:
                        info_placeholder.error("❌ Unable to capture frame. Check your camera.")
                    
                    frame_count += 1
                    
                    # Check if session state was changed (Stop button clicked)
                    if not st.session_state.camera_active:
                        break
                    
                    # Auto-stop after 60 seconds
                    elapsed = time.time() - start_time
                    if elapsed > 60:
                        st.session_state.camera_active = False
                        if st.session_state.detector:
                            st.session_state.detector.release()
                        st.session_state.detector = None
                        st.session_state.camera_start_time = None
                        st.rerun()
                        break
                    
                    # Small delay between frames (33ms = ~30fps)
                    time.sleep(0.033)
                    
                except Exception as e:
                    info_placeholder.error(f"Error: {str(e)}")
                    break
        else:
            st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; height: 400px; background: rgba(255,255,255,0.1); border-radius: 20px;">
                <div style="text-align: center;">
                    <p style="font-size: 4rem;">📷</p>
                    <p style="font-size: 1.2rem; color: #e0e0e0;">Click "Start Camera" to begin emotion detection</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

#  AUTH
elif selected == "Auth":
    st.markdown("""
    <div class="auth-section" id="auth">
        <h2>Join EmoRecs</h2>
        <p>Create an account to get personalized, emotion-aware recommendations powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="signup-card">
            <h3> Sign Up</h3>
            <p>New here? Create your EmoRecs account.</p>
        </div>
        """, unsafe_allow_html=True)
        name = st.text_input("User Name", key="signup_name", placeholder="Full Name")
        email = st.text_input("Email", key="signup_email", placeholder="Email")
        password = st.text_input("Password", type="password", key="signup_password", placeholder="Password")
        
        if st.button("Create Account", key="signup_btn"):
            if name and email and password:
                success, message = database.register_user(name, email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields!")
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3> Login</h3>
            <p>Access your personalized Emotion-Based Recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        email_login = st.text_input("Email", key="login_email", placeholder="Email")
        password_login = st.text_input("Password", type="password", key="login_password", placeholder="Password")
        
        if st.button("Login", key="login_btn"):
            if email_login and password_login:
                success, user_data, message = database.login_user(email_login, password_login)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['id']
                    st.session_state.username = user_data['username']
                    st.session_state.email = user_data['email']
                    # Fetch additional profile data from database
                    profile_data = database.get_user_profile(user_data['id'])
                    if profile_data:
                        st.session_state.age = profile_data.get('age')
                        st.session_state.avatar = profile_data.get('avatar')
                    st.session_state.redirect_to = "Detect Emotion"  # Redirect to camera after login
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter email and password!")

# DASHBOARD
elif selected == "Dashboard":
    st.markdown("""
    <div class="auth-section">
        <h2>👤 My Dashboard</h2>
        <p>Welcome back, """ + st.session_state.username + """!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info card
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📧 Account Info</h3>
            <p><strong>Username:</strong> """ + st.session_state.username + """</p>
            <p><strong>Email:</strong> """ + st.session_state.email + """</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3> Quick Actions</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.rerun()
    
    # User activity
    st.markdown("""
    <div class="features-section">
        <h2>📊 My Activity</h2>
    </div>
    """, unsafe_allow_html=True)
    
    activities = database.get_user_activity(st.session_state.user_id)
    if activities:
        for activity in activities[:10]:
            st.markdown(f"""
            <div class="step">
                <h4>{activity['action']}</h4>
                <p>{activity['details']} - {activity['timestamp']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity yet!")

# ADMIN
elif selected == "Admin":
    st.markdown("""
    <div class="auth-section">
        <h2> Admin Dashboard</h2>
        <p>View all registered users and system data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get stats
    stats = database.get_database_stats()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", stats.get('total_users', 0))
    with col2:
        st.metric("Total Activities", stats.get('total_activities', 0))
    with col3:
        st.metric("Emotion Logs", stats.get('total_emotion_logs', 0))
    with col4:
        st.metric("New Users (7 days)", stats.get('new_users_7days', 0))
    
    # Tabs for data
    tab1, tab2, tab3 = st.tabs(["📋 Users", "📝 Activity Logs", "😊 Emotion Logs"])
    
    with tab1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 20px; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
            <h3 style="color: #ffffff !important; font-weight: bold; font-size: 1.4rem; margin-bottom: 15px; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">📋 Registered Users</h3>
        """, unsafe_allow_html=True)
        users = database.get_all_users()
        if users:
            import pandas as pd
            df = pd.DataFrame(users)
            # Style the dataframe with dark background and light text
            st.markdown("""
            <style>
            div[data-testid="stDataFrame"] {
                background: linear-gradient(135deg, #2d1b4e 0%, #1e1e2f 100%) !important;
                border-radius: 10px !important;
                border: 1px solid rgba(108, 99, 255, 0.3);
            }
            div[data-testid="stDataFrame"] table {
                background: transparent !important;
            }
            div[data-testid="stDataFrame"] thead tr {
                background: linear-gradient(135deg, #6c63ff, #00d2ff) !important;
            }
            div[data-testid="stDataFrame"] thead th {
                background: linear-gradient(135deg, #6c63ff, #00d2ff) !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                border-bottom: 2px solid rgba(255, 255, 255, 0.3) !important;
            }
            div[data-testid="stDataFrame"] tbody td {
                background: rgba(255, 255, 255, 0.1) !important;
                color: #ffffff !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            div[data-testid="stDataFrame"] tbody tr:hover td {
                background: rgba(108, 99, 255, 0.3) !important;
            }
            div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
                background: rgba(255, 255, 255, 0.05) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users registered yet!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<h3 style='color: #ffffff !important;'>📝 User Activity</h3>", unsafe_allow_html=True)
        activities = database.get_user_activity()
        if activities:
            import pandas as pd
            df = pd.DataFrame(activities)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No activity recorded yet!")
    
    with tab3:
        st.markdown("Emotion Detection Logs")
        emotion_logs = database.get_emotion_logs()
        if emotion_logs:
            import pandas as pd
            df = pd.DataFrame(emotion_logs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No emotion logs recorded yet!")


# FOOTER
st.markdown("""
<hr style="border: 1px solid rgba(255, 255, 255, 0.2); margin-top: 40px;">
<footer>© 2026 EmoRecs · Emotion-Based Recommendation System</footer>""", unsafe_allow_html=True)
