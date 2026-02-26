import streamlit as st
import streamlit_option_menu
import database
import camera_detection

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

# Sidebar navigation
st.sidebar.title(" 1.Navigation")
sidebar_selection = st.sidebar.radio("Go to:", sidebar_options, index=sidebar_options.index(st.session_state.sidebar_selected))

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
            <h3>🎮 Camera Controls</h3>
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
                    st.rerun()
                else:
                    st.error(message)
        else:
            if st.button("⏹️ Stop Camera", key="stop_camera"):
                if st.session_state.detector:
                    st.session_state.detector.release()
                st.session_state.detector = None
                st.session_state.camera_active = False
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
            # Get camera frame
            success, frame = st.session_state.detector.get_frame()
            
            if success and frame is not None:
                # Process frame for face detection
                processed_frame, faces = st.session_state.detector.process_frame(frame)
                
                # Convert to image for display
                img = camera_detection.convert_frame_to_image(processed_frame)
                st.image(img, caption="Live Camera Feed - Face Detection", use_container_width=True)
                
                # Display detection results
                if len(faces) > 0:
                    st.success(f"✓ Detected {len(faces)} face(s)!")
                else:
                    st.warning("No face detected. Please position your face in the frame.")
            else:
                st.error("Unable to capture frame. Please check your camera.")
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
        <h2>🛡️ Admin Dashboard</h2>
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
        st.markdown("Registered Users")
        users = database.get_all_users()
        if users:
            import pandas as pd
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users registered yet!")
    
    with tab2:
        st.markdown(" User Activity")
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
