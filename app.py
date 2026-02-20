import streamlit as st
import streamlit_option_menu


# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="EmoRecs | Emotion-Based Recommendation System",
    page_icon="😊",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------s
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: 
        radial-gradient(1200px 600px at 10% 10%, rgba(108, 99, 255, 0.25), transparent 40%),
        radial-gradient(1000px 500px at 90% 20%, rgba(0, 210, 255, 0.25), transparent 40%),
        linear-gradient(180deg, #0b0e2b 0%, #0f1226 100%);
    color: #f5f7ff !important;
}

/* Force white background override for visibility */
[data-testid="stApp"] {
    background: 
        radial-gradient(1200px 600px at 10% 10%, rgba(108, 99, 255, 0.25), transparent 80%),
        radial-gradient(1000px 500px at 90% 20%, rgba(0, 210, 255, 0.25), transparent 80%),
        linear-gradient(180deg, #0b0e2b 0%, #0f1226 100%) !important;
    color: #f5f7ff !important;
}

/* Header Styles */
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 8%;s
    
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 700;
    font-size: 1.2rem;
    color: #f5f7ff !important;
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
    color: #f5f7ff !important;
    opacity: 0.85;
    font-weight: 400;
}

nav a:hover {
    opacity: 1;
    color: #ffffff !important;
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
    color: #f5f7ff !important;
}

.hero p {
    font-size: 1.05rem;
    opacity: 0.9;
    max-width: 520px;
    margin-bottom: 32px;
    color: #e0e0e0 !important;
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
    color: #f5f7ff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.3s;
}

.btn-outline:hover {
    border-color: rgba(255, 255, 255, 0.6);
}

/* Visual Section */
.visual {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.35);
}

.visual h3 {
    margin-bottom: 16px;
    font-weight: 600;
    color: #f5f7ff !important;
}

.emotion-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}

.emotion {
    padding: 18px 12px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.08);
    text-align: center;
    font-size: 0.9rem;
    color: #e0e0e0 !important;
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

# -------------------- HEADER --------------------
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
    <nav>
        <a href="#features" style="margin-left: 28px; text-decoration: none; color: #f5f7ff; opacity: 0.85;">Features</a>
        <a href="#how" style="margin-left: 28px; text-decoration: none; color: #f5f7ff; opacity: 0.85;">How it Works</a>
    </nav>
</div>
""", unsafe_allow_html=True)

# -------------------- NAVIGATION --------------------
selected = streamlit_option_menu.option_menu(
    menu_title=None,
    options=["Home", "Features", "How It Works", "Auth"],
    icons=["house", "stars", "diagram-3", "person-circle"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {"padding": "0"},
        "nav-link": {"color": "#070E9EB1", "opacity": "0.85"},
        "nav-link-selected": {"background": "linear-gradient(135deg, #6c63ff, #00d2ff)", "opacity": "1"},
    }
)

# -------------------- HOME --------------------
if selected == "Home":
    # Hero Section
    st.markdown("""
    <div style="padding: 80px 8% 120px; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 48px; align-items: center;">
        <div>
            <h1 style="font-size: 3rem; line-height: 1.2; margin-bottom: 20px; color: #f5f7ff;">Emotion-Based<br>Smart Recommendations</h1>
            <p style="font-size: 1.05rem; opacity: 0.9; max-width: 520px; margin-bottom: 32px; color: #e0e0e0;">
                EmoRecs detects your real-time facial emotions using AI and computer vision,
                then recommends movies, music, games, and books that truly match how you feel.
            </p>
            <div style="display: flex; gap: 16px;">
                <button class="btn-primary">Get Started</button>
                <button class="btn-outline">View Demo</button>
            </div>
        </div>
        <div class="visual">
            <h3>Detected Emotions</h3>
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

# -------------------- FEATURES --------------------
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

# -------------------- HOW IT WORKS --------------------
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
                <h4>2. Analyze Mood</h4>
                <p>AI models classify emotions using trained datasets.</p>
            </div>
            <div class="step">
                <h4>3. Recommend Content</h4>
                <p>Relevant movies, music, games, and books are suggested instantly.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- AUTH --------------------
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
            <h3>✨ Sign Up</h3>
            <p>New here? Create your EmoRecs account.</p>
        </div>
        """, unsafe_allow_html=True)
        name = st.text_input("User Name", key="signup_name", placeholder="Full Name")
        email = st.text_input("Email", key="signup_email", placeholder="Email")
        password = st.text_input("Password", type="password", key="signup_password", placeholder="Password")
        
        if st.button("Create Account", key="signup_btn"):
            st.success("Account created successfully!")
        
        st.markdown("""
        <p class="terms">By signing up, you agree to our <a href="#">Terms</a> & <a href="#">Privacy Policy</a>.</p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔐 Login</h3>
            <p>Access your personalized Emotion-Based Recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        email_login = st.text_input("Email", key="login_email", placeholder="Email")
        password_login = st.text_input("Password", type="password", key="login_password", placeholder="Password")
        
        if st.button("Login", key="login_btn"):
            st.success("Login successful!")
        
        st.markdown("""
        <p class="terms">Forgot password? <a href="#">Reset</a></p>
        """, unsafe_allow_html=True)

# -------------------- FOOTER --------------------
st.markdown("""
<hr style="border: 1px solid rgba(255, 255, 255, 0.2); margin-top: 40px;">
<footer>© 2026 EmoRecs · Emotion-Based Recommendation System</footer>""", unsafe_allow_html=True)
