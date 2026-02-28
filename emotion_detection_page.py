"""
Emotion Detection Page for EmoRecs
───────────────────────────────────
• OpenCV  → webcam capture (cv2.VideoCapture with CAP_DSHOW on Windows)
• Haarcascade → face detection
• DeepFace → CNN-based emotion classification (FER-2013 weights)
• Streamlit → live video feed, Start/Stop buttons, emotion cards
• SQLite3  → saves detected emotion to the database
"""

import streamlit as st
import cv2
import numpy as np
import time
from collections import Counter
import database


# ━━━━━━━━━━━━━━  CONSTANTS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMOTION_EMOJI = {
    "angry":    "😠",
    "disgust":  "🤢",
    "fear":     "😨",
    "happy":    "😊",
    "sad":      "😢",
    "surprise": "😲",
    "neutral":  "😐",
}

EMOTION_COLORS = {
    "angry":    (0, 0, 255),
    "disgust":  (0, 140, 255),
    "fear":     (180, 105, 255),
    "happy":    (0, 255, 0),
    "sad":      (255, 165, 0),
    "surprise": (0, 255, 255),
    "neutral":  (200, 200, 200),
}

ANALYSE_EVERY_N_FRAMES = 10
DB_LOG_COOLDOWN = 5.0


# ━━━━━━━━━━━━━━  MODEL LOADER (cached)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_resource(show_spinner="🔄 Loading emotion detection model …")
def _load_models():
    """Load Haarcascade + DeepFace Emotion model (cached once)."""
    from deepface import DeepFace

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    DeepFace.build_model(task="facial_attribute", model_name="Emotion")
    return face_cascade, DeepFace


# ━━━━━━━━━━━━━━  OPEN CAMERA (cached per session)  ━━━━━━━━━━━━━━━━━
@st.cache_resource(show_spinner="📷 Opening camera …")
def _get_camera():
    """
    Open the webcam and cache it so it stays open across Streamlit reruns.
    Tries CAP_DSHOW first (required on most Windows devices), then fallbacks.
    """
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            # Read a few warm-up frames (some cameras return black initially)
            for _ in range(5):
                cap.read()
            return cap
        cap.release()

    # Last resort
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        for _ in range(5):
            cap.read()
        return cap

    return None


def _release_camera():
    """Release the cached camera and clear the cache."""
    _get_camera.clear()


# ━━━━━━━━━━━━━━  EMOTION ANALYSER  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _analyse_emotion(deepface_module, face_bgr):
    """Run DeepFace emotion analysis on a cropped BGR face image."""
    try:
        result = deepface_module.analyze(
            face_bgr,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(result, list):
            result = result[0]
        dominant = result["dominant_emotion"]
        scores = result["emotion"]
        conf = scores[dominant] / 100.0
        return dominant, conf, scores
    except Exception:
        return "neutral", 0.0, {}


# ━━━━━━━━━━━━━━  DRAW BOUNDING BOX  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _draw_fancy_box(img, x, y, w, h, color, label):
    """Draw corner-style bounding box with label."""
    t = 2
    c = min(20, w // 4, h // 4)
    cv2.line(img, (x, y), (x + c, y), color, t)
    cv2.line(img, (x, y), (x, y + c), color, t)
    cv2.line(img, (x + w, y), (x + w - c, y), color, t)
    cv2.line(img, (x + w, y), (x + w, y + c), color, t)
    cv2.line(img, (x, y + h), (x + c, y + h), color, t)
    cv2.line(img, (x, y + h), (x, y + h - c), color, t)
    cv2.line(img, (x + w, y + h), (x + w - c, y + h), color, t)
    cv2.line(img, (x + w, y + h), (x + w, y + h - c), color, t)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    cv2.rectangle(img, (x, y - th - 14), (x + tw + 10, y), color, -1)
    cv2.putText(img, label, (x + 5, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)


# ━━━━━━━━━━━━━━  EMOTION RESULT CARD  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _render_emotion_card(container, emotion, confidence, scores, history):
    """Render styled emotion result card."""
    emoji = EMOTION_EMOJI.get(emotion, "🤔")
    bars = ""
    for emo in ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]:
        pct = scores.get(emo, 0)
        e = EMOTION_EMOJI.get(emo, "")
        bar_color = "#6c63ff" if emo == emotion else "rgba(255,255,255,0.18)"
        fw = "700" if emo == emotion else "400"
        bars += f"""
        <div style="display:flex;align-items:center;gap:8px;margin:5px 0;">
            <span style="width:100px;font-size:0.85rem;font-weight:{fw};">{e} {emo.capitalize()}</span>
            <div style="flex:1;background:rgba(255,255,255,0.08);border-radius:6px;height:16px;overflow:hidden;">
                <div style="width:{pct:.1f}%;background:{bar_color};height:100%;border-radius:6px;"></div>
            </div>
            <span style="width:50px;text-align:right;font-size:0.8rem;">{pct:.1f}%</span>
        </div>"""

    chips = ""
    for h_emo in history[-8:]:
        h_e = EMOTION_EMOJI.get(h_emo, "")
        chips += (f'<span style="display:inline-block;background:rgba(255,255,255,0.12);'
                  f'border-radius:12px;padding:3px 10px;margin:2px;font-size:0.78rem;">'
                  f'{h_e} {h_emo.capitalize()}</span>')

    container.markdown(f"""
    <div style="background:rgba(255,255,255,0.10);backdrop-filter:blur(14px);
                border-radius:20px;padding:28px;margin-top:18px;
                box-shadow:0 12px 48px rgba(0,0,0,0.30);border:1px solid rgba(108,99,255,0.25);">
        <h2 style="text-align:center;color:#f5f7ff;margin:0 0 2px;">{emoji} {emotion.capitalize()}</h2>
        <p style="text-align:center;color:#c0c0c0;margin-bottom:18px;font-size:0.95rem;">
            Confidence: <b style="color:#6c63ff;">{confidence:.0%}</b></p>
        {bars}
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:14px 0 10px;">
        <p style="font-size:0.8rem;color:#aaa;margin-bottom:6px;">Recent detections:</p>
        <div style="display:flex;flex-wrap:wrap;">{chips}</div>
    </div>""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━  MAIN  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    """Emotion Detection page — called from app.py."""

    st.markdown("""
    <div style="text-align:center;padding:24px 0 12px;">
        <h1 style="color:#f5f7ff;margin-bottom:4px;">😊 Emotion Detection</h1>
        <p style="color:#c8c8c8;font-size:1.05rem;max-width:600px;margin:0 auto;">
            Click <b>Start Camera</b> to open your webcam. EmoRecs will detect
            your face and recognise your emotion in real-time.
        </p>
    </div>""", unsafe_allow_html=True)

    # Session state defaults
    for key, val in {
        "camera_running": False,
        "last_emotion": None,
        "last_confidence": 0.0,
        "last_scores": {},
        "emotion_history": [],
        "detected_emotion": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Buttons
    btn1, btn2, _ = st.columns([1, 1, 3])
    with btn1:
        start_clicked = st.button("📷  Start Camera", key="ed_start_btn", use_container_width=True)
    with btn2:
        stop_clicked = st.button("⏹  Stop Camera", key="ed_stop_btn", use_container_width=True)

    if start_clicked:
        st.session_state.camera_running = True
        st.session_state.emotion_history = []
        st.session_state.detected_emotion = None
    if stop_clicked:
        st.session_state.camera_running = False
        _release_camera()

    # Placeholders
    status_ph = st.empty()
    frame_ph = st.empty()
    emotion_ph = st.empty()

    # ── Camera OFF ────────────────────────────────────────────────────
    if not st.session_state.camera_running:
        if st.session_state.last_emotion:
            status_ph.info("⏹ Camera stopped. Last detected emotion shown below.")
            _render_emotion_card(
                emotion_ph,
                st.session_state.last_emotion,
                st.session_state.last_confidence,
                st.session_state.last_scores,
                st.session_state.emotion_history,
            )
            st.session_state.detected_emotion = st.session_state.last_emotion
        else:
            frame_ph.markdown("""
            <div style="text-align:center;padding:80px 20px;
                        background:rgba(255,255,255,0.06);border-radius:16px;
                        border:2px dashed rgba(108,99,255,0.35);">
                <p style="font-size:3rem;margin:0;">📷</p>
                <p style="color:#c0c0c0;font-size:1rem;margin-top:8px;">
                    Camera is off. Click <b>Start Camera</b> to begin.
                </p>
            </div>""", unsafe_allow_html=True)
        return

    # ── Camera ON ─────────────────────────────────────────────────────
    face_cascade, DeepFace = _load_models()

    cap = _get_camera()
    if cap is None or not cap.isOpened():
        frame_ph.error("❌ Could not open webcam. Make sure your camera is connected "
                       "and not in use by another application.")
        st.session_state.camera_running = False
        _release_camera()
        return

    status_ph.success("🟢 Camera is running — detecting emotions …")

    frame_count = 0
    dominant_emotion = st.session_state.last_emotion
    confidence = st.session_state.last_confidence
    scores = st.session_state.last_scores
    last_db_log_time = 0.0

    try:
        while st.session_state.camera_running:
            ret, frame = cap.read()
            if not ret:
                # Try reopening
                _release_camera()
                cap = _get_camera()
                if cap is None or not cap.isOpened():
                    frame_ph.error("❌ Lost camera feed.")
                    break
                continue

            frame = cv2.flip(frame, 1)
            display = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5,
                minSize=(60, 60), flags=cv2.CASCADE_SCALE_IMAGE,
            )

            for (x, y, w, h) in faces:
                if frame_count % ANALYSE_EVERY_N_FRAMES == 0:
                    face_crop = frame[y:y+h, x:x+w]
                    dominant_emotion, confidence, scores = _analyse_emotion(DeepFace, face_crop)
                    st.session_state.last_emotion = dominant_emotion
                    st.session_state.last_confidence = confidence
                    st.session_state.last_scores = scores
                    st.session_state.emotion_history.append(dominant_emotion)

                    now = time.time()
                    if (now - last_db_log_time) >= DB_LOG_COOLDOWN:
                        user_id = st.session_state.get("user_id")
                        if user_id:
                            database.log_emotion_detection(user_id, dominant_emotion, confidence)
                            database.log_user_activity(
                                user_id, "emotion_detection",
                                f"Detected emotion: {dominant_emotion} ({confidence:.0%})",
                            )
                        last_db_log_time = now

                if dominant_emotion:
                    color = EMOTION_COLORS.get(dominant_emotion, (200, 200, 200))
                    emoji = EMOTION_EMOJI.get(dominant_emotion, "")
                    label = f"{emoji} {dominant_emotion.capitalize()} {confidence:.0%}"
                    _draw_fancy_box(display, x, y, w, h, color, label)
                else:
                    cv2.rectangle(display, (x, y), (x+w, y+h), (200, 200, 200), 2)

            rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            frame_ph.image(rgb, channels="RGB", use_container_width=True)

            if dominant_emotion and scores:
                _render_emotion_card(emotion_ph, dominant_emotion, confidence, scores,
                                     st.session_state.emotion_history)

            frame_count += 1
            time.sleep(0.033)

    except Exception as e:
        status_ph.error(f"⚠️ Camera error: {e}")
    finally:
        status_ph.info("⏹ Camera stopped.")
        if dominant_emotion:
            st.session_state.detected_emotion = dominant_emotion
            user_id = st.session_state.get("user_id")
            if user_id and st.session_state.emotion_history:
                most_common = Counter(st.session_state.emotion_history).most_common(1)[0][0]
                database.save_dominant_emotion(user_id, most_common)


def get_detected_emotion():
    """Return the last detected dominant emotion for recommendation logic."""
    return st.session_state.get("detected_emotion")


if __name__ == "__main__":
    main()
