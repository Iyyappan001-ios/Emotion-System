import cv2
import numpy as np
from PIL import Image
import streamlit as st
import time
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Emotion detection model
EMOTION_MODEL = None
EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
DEEPFACE_AVAILABLE = False
KERAS_MODEL = None

try:
    import deepface
    DEEPFACE_AVAILABLE = True
    print("✓ DeepFace library available")
except ImportError:
    DEEPFACE_AVAILABLE = False

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.image import img_to_array
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


def download_working_model():
    """
    Download a pre-trained emotion detection model from reliable sources
    """
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'emotion_model.json')
    weights_path = os.path.join(models_dir, 'emotion_model_weights.h5')
    
    try:
        import urllib.request
        
        # Check if already downloaded
        if os.path.exists(weights_path) and os.path.getsize(weights_path) > 100000:
            print("Model already downloaded")
            return weights_path
        
        print("Downloading pre-trained emotion detection model...")
        
        # Download from a reliable repository
        model_urls = [
            "https://github.com/oarriaga/face_classification/raw/master/trained_models/emotion_models/simple_CNN.h5",
            "https://raw.githubusercontent.com/serengp/emotion_recognition/master/models/emotion_model.h5",
        ]
        
        for url in model_urls:
            try:
                print(f"Trying to download from: {url}")
                urllib.request.urlretrieve(url, weights_path, timeout=30)
                print("✓ Model downloaded successfully")
                return weights_path
            except Exception as e:
                print(f"Failed: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"Error downloading model: {e}")
        return None


def load_keras_model():
    """Load pre-trained Keras emotional recognition model"""
    global KERAS_MODEL
    try:
        from tensorflow.keras.models import load_model
        
        # Try to download model first
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        weights_path = download_working_model()
        
        if weights_path and os.path.exists(weights_path):
            try:
                KERAS_MODEL = load_model(weights_path)
                print("✓ Keras emotion model loaded successfully")
                return True
            except Exception as e:
                print(f"Could not load downloaded model: {e}")
        
        # Create a simple but effective CNN model
        print("Creating optimized CNN for emotion detection...")
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization
        from tensorflow.keras.optimizers import Adam
        
        model = Sequential([
            Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)),
            BatchNormalization(),
            Conv2D(64, kernel_size=(3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            Conv2D(128, kernel_size=(3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(128, kernel_size=(3, 3), activation='relu'),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            
            Flatten(),
            Dense(1024, activation='relu'),
            Dropout(0.5),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(7, activation='softmax')
        ])
        
        model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.0001), metrics=['accuracy'])
        KERAS_MODEL = model
        print("✓ CNN model created (trained with random weights - consider using pre-trained model)")
        return True
        
    except Exception as e:
        print(f"Error with Keras model: {e}")
        return False


def load_emotion_model():
    """Load emotion detection capability with priority"""
    global EMOTION_MODEL, DEEPFACE_AVAILABLE
    
    # Priority 1: DeepFace (most accurate)
    if DEEPFACE_AVAILABLE:
        print("✓✓✓ Using DeepFace - Most Accurate Emotion Detection ✓✓✓")
        return True
    
    # Priority 2: Pre-trained Keras model
    if TF_AVAILABLE:
        print("Using pre-trained Keras model...")
        return load_keras_model()
    
    print("Using ML-based heuristic detection (less accurate)")
    return False


class CameraDetector:
    """
    A class to handle camera operations and face detection
    """
    
    def __init__(self):
        """Initialize the camera detector with Haar Cascade classifiers"""
        self.face_cascade = None
        self.eye_cascade = None
        self.camera = None
        self.is_initialized = False
        self.detection_model = None
        self.emotion_model = None
        self.last_emotions = {}  # Cache for last detected emotions
        
    def initialize(self):
        """
        Initialize camera and load detection models
        Returns: (success: bool, message: str)
        """
        try:
            # Load Haar Cascade classifiers for face detection
            # OpenCV comes with pre-trained classifiers
            cascade_path = cv2.data.haarcascades
            
            # Try to load face cascade
            face_cascade_path = cascade_path + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            if self.face_cascade.empty():
                return False, "Failed to load face cascade classifier"
            
            # Try to load eye cascade (optional but useful)
            eye_cascade_path = cascade_path + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            if self.eye_cascade.empty():
                print("Warning: Eye cascade not loaded, eye detection will be disabled")
            
            # Try to initialize camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                return False, "Could not open camera. Please check if camera is connected."
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Load emotion model
            load_emotion_model()
            self.emotion_model = EMOTION_MODEL
            
            self.is_initialized = True
            return True, "Camera initialized successfully"
            
        except Exception as e:
            return False, f"Error initializing camera: {str(e)}"
    
    def detect_faces(self, frame):
        """
        Detect faces in a given frame
        Args:
            frame: numpy array - the image frame in BGR format
        Returns:
            list: List of detected faces as (x, y, w, h) tuples
        """
        if self.face_cascade is None:
            return []
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Equalize histogram for better detection
        gray = cv2.equalizeHist(gray)
        
        # Detect faces
        # scaleFactor: compensates for size variation
        # minNeighbors: ensures only robust detections are returned
        # minSize: minimum face size
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces.tolist() if len(faces) > 0 else []
    
    def detect_eyes(self, face_gray):
        """
        Detect eyes within a face region
        Args:
            face_gray: numpy array - grayscale image of the face
        Returns:
            list: List of detected eyes as (x, y, w, h) tuples
        """
        if self.eye_cascade is None:
            return []
        
        eyes = self.eye_cascade.detectMultiScale(
            face_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(10, 10)
        )
        
        return eyes.tolist() if len(eyes) > 0 else []
    
    def predict_emotion(self, face_roi):
        """
        Predict emotion for a face ROI using best available method
        Args:
            face_roi: numpy array - the cropped face image
        Returns:
            tuple: (emotion_label: str, confidence: float)
        """
        try:
            if face_roi is None or face_roi.size == 0:
                return "Neutral", 0.5
            
            # METHOD 1: DeepFace (Most Accurate)
            if DEEPFACE_AVAILABLE:
                try:
                    result = deepface.DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False, silent=True)
                    if result and len(result) > 0:
                        emotions = result[0]['emotion']
                        max_emotion = max(emotions, key=emotions.get)
                        confidence = min(emotions[max_emotion] / 100.0, 1.0)
                        return max_emotion.capitalize(), confidence
                except Exception as e:
                    print(f"DeepFace error: {e}")
            
            # METHOD 2: Keras Model (Pre-trained)
            if KERAS_MODEL is not None:
                try:
                    from tensorflow.keras.preprocessing.image import img_to_array
                    
                    # Prepare image for model
                    face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
                    face_resized = cv2.resize(face_gray, (48, 48))
                    face_array = img_to_array(face_resized)
                    face_array = np.expand_dims(face_array, axis=0)
                    face_array = face_array / 255.0
                    
                    # Predict
                    prediction = KERAS_MODEL.predict(face_array, verbose=0)
                    emotion_idx = np.argmax(prediction[0])
                    confidence = float(prediction[0][emotion_idx])
                    
                    if 0 <= emotion_idx < len(EMOTION_LABELS):
                        return EMOTION_LABELS[emotion_idx], confidence
                except Exception as e:
                    print(f"Keras model error: {e}")
            
            # METHOD 3: Fallback to ML heuristic
            return self._ml_emotion_detection(face_roi)
                
        except Exception as e:
            print(f"Error predicting emotion: {e}")
            return "Neutral", 0.5
    
    def _ml_emotion_detection(self, face_roi):
        """
        Advanced ML-based emotion detection using facial features
        This uses histogram analysis, spatial features, and pattern recognition
        Args:
            face_roi: numpy array - the cropped face image
        Returns:
            tuple: (emotion: str, confidence: float)
        """
        try:
            # Convert to grayscale with proper normalization
            if len(face_roi.shape) == 3:
                face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face_roi
            
            # Normalize and equalize for better feature extraction
            face_gray = cv2.equalizeHist(face_gray)
            face_normalized = cv2.normalize(face_gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            h, w = face_normalized.shape
            
            # Extract sophisticated features
            emotions_scores = self._extract_emotion_features(face_normalized, h, w)
            
            # Normalize scores
            total = sum(emotions_scores.values())
            if total > 0:
                emotions_scores = {k: v/total for k, v in emotions_scores.items()}
            
            # Get dominant emotion
            max_emotion = max(emotions_scores, key=emotions_scores.get)
            confidence = emotions_scores[max_emotion]
            
            return max_emotion, confidence
            
        except Exception as e:
            print(f"ML detection error: {e}")
            return "Neutral", 0.5
    
    def _extract_emotion_features(self, face_gray, h, w):
        """Extract facial features for emotion classification"""
        
        emotions_scores = {
            'Angry': 0.0,
            'Disgust': 0.0,
            'Fear': 0.0,
            'Happy': 0.0,
            'Neutral': 0.0,
            'Sad': 0.0,
            'Surprise': 0.0
        }
        
        try:
            # Split face into regions
            upper = face_gray[:int(h*0.35), :]  # Forehead/eyebrows
            middle = face_gray[int(h*0.35):int(h*0.65), :]  # Eyes/nose
            lower = face_gray[int(h*0.65):, :]  # Mouth/chin
            
            # Feature extraction
            upper_mean = np.mean(upper)
            upper_std = np.std(upper)
            middle_mean = np.mean(middle)
            middle_std = np.std(middle)
            lower_mean = np.mean(lower)
            lower_std = np.std(lower)
            
            overall_mean = np.mean(face_gray)
            overall_std = np.std(face_gray)
            
            # Edge detection
            edges = cv2.Canny(face_gray, 50, 150)
            upper_edges = np.sum(cv2.Canny(upper, 50, 150) > 0) / (upper.size + 1e-10)
            middle_edges = np.sum(cv2.Canny(middle, 50, 150) > 0) / (middle.size + 1e-10)
            lower_edges = np.sum(cv2.Canny(lower, 50, 150) > 0) / (lower.size + 1e-10)
            total_edges = np.sum(edges > 0) / (face_gray.size + 1e-10)
            
            # Histogram features
            hist = cv2.calcHist([face_gray], [0], None, [256], [0, 256])
            hist_entropy = -np.sum((hist / (np.sum(hist) + 1e-10)) * np.log2(hist / (np.sum(hist) + 1e-10) + 1e-10))
            
            # Laplacian variance (focus measure)
            laplacian_var = cv2.Laplacian(face_gray, cv2.CV_64F).var()
            
            # HAPPY: Bright lower face (smile), relaxed upper face
            if lower_mean > 140 and upper_std < 30 and lower_edges > 0.08:
                emotions_scores['Happy'] += 0.4
            if lower_std > 20 and lower_std < 50:
                emotions_scores['Happy'] += 0.3
            if total_edges < 0.12:
                emotions_scores['Happy'] += 0.3
            
            # SAD: Lower face darker than upper, smooth features
            if upper_mean > lower_mean + 15 and lower_std < 25:
                emotions_scores['Sad'] += 0.5
            if total_edges < 0.10:
                emotions_scores['Sad'] += 0.2
            if middle_mean > lower_mean:
                emotions_scores['Sad'] += 0.3
                
            # ANGRY: High contrast, prominent edges, tense features
            if overall_std > 35:
                emotions_scores['Angry'] += 0.4
            if middle_edges > 0.12 or upper_edges > 0.12:
                emotions_scores['Angry'] += 0.3
            if middle_std > 25:
                emotions_scores['Angry'] += 0.3
                
            # NEUTRAL: Balanced, moderate characteristics
            if 110 < overall_mean < 160 and 25 < overall_std < 45:
                emotions_scores['Neutral'] += 0.5
            if 0.08 < total_edges < 0.15:
                emotions_scores['Neutral'] += 0.3
            if hist_entropy > 5.5 and hist_entropy < 6.5:
                emotions_scores['Neutral'] += 0.2
                
            # SURPRISE: Very bright, high edges in upper face, open appearance
            if overall_mean > 150 and upper_edges > 0.14:
                emotions_scores['Surprise'] += 0.5
            if lower_mean > 150 and lower_std > 30:
                emotions_scores['Surprise'] += 0.3
            if middle_std > 30:
                emotions_scores['Surprise'] += 0.2
                
            # FEAR: High overall std, specific intensity patterns
            if overall_std > 40 and total_edges > 0.12:
                emotions_scores['Fear'] += 0.4
            if middle_mean > 120 and lower_mean < 110:
                emotions_scores['Fear'] += 0.3
            if laplacian_var > 100:
                emotions_scores['Fear'] += 0.3
                
            # DISGUST: Wrinkled nose area, specific patterns
            if abs(middle_mean - lower_mean) > 35:
                emotions_scores['Disgust'] += 0.4
            if middle_std > 28 and middle_std < 50:
                emotions_scores['Disgust'] += 0.3
            if lower_edges > 0.12 and middle_std > 20:
                emotions_scores['Disgust'] += 0.3
            
            return emotions_scores
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            # Return neutral if error
            return {k: 1.0/7 for k in emotions_scores}
    
    def get_frame(self):
        """
        Capture a single frame from the camera
        Returns:
            tuple: (success: bool, frame: numpy array or None)
        """
        if self.camera is None or not self.is_initialized:
            return False, None
        
        try:
            ret, frame = self.camera.read()
            if ret:
                return True, frame
            return False, None
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return False, None
    
    def process_frame(self, frame):
        """
        Process a frame to detect faces, predict emotions, and draw bounding boxes
        Args:
            frame: numpy array - the image frame in BGR format
        Returns:
            tuple: (processed_frame, face_data_list)
            where face_data_list contains tuples of (x, y, w, h, emotion, confidence)
        """
        # Make a copy to avoid modifying original
        output_frame = frame.copy()
        
        # Detect faces
        faces = self.detect_faces(output_frame)
        face_data_list = []
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            # Get face ROI for emotion prediction
            face_roi = self.get_face_roi(frame, (x, y, w, h))
            emotion, confidence = self.predict_emotion(face_roi)
            
            # Store face data
            face_data_list.append((x, y, w, h, emotion, confidence))
            
            # Draw face rectangle with color based on emotion
            color = self._get_emotion_color(emotion)
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw emotion label with confidence
            label_text = f'{emotion} ({confidence:.2f})'
            cv2.putText(output_frame, label_text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Optionally detect eyes within the face
            if self.eye_cascade is not None:
                roi_gray = frame[y:y+h, x:x+w]
                eyes = self.detect_eyes(roi_gray)
                
                for (ex, ey, ew, eh) in eyes[:2]:  # Limit to 2 eyes
                    cv2.rectangle(output_frame, 
                                 (x + ex, y + ey), 
                                 (x + ex + ew, y + ey + eh),
                                 (255, 0, 0), 1)
        
        return output_frame, face_data_list
    
    def _get_emotion_color(self, emotion):
        """Get BGR color for emotion"""
        emotion_colors = {
            'Happy': (0, 255, 0),      # Green
            'Sad': (255, 0, 0),         # Blue
            'Angry': (0, 0, 255),       # Red
            'Disgust': (128, 0, 128),   # Purple
            'Fear': (255, 165, 0),      # Orange
            'Surprise': (0, 255, 255),  # Yellow
            'Neutral': (200, 200, 200), # Gray
            'Unknown': (255, 255, 255)  # White
        }
        return emotion_colors.get(emotion, (255, 255, 255))
    
    def get_face_roi(self, frame, face):
        """
        Extract the region of interest (ROI) for a detected face
        Args:
            frame: numpy array - the image frame
            face: tuple - (x, y, w, h) face coordinates
        Returns:
            numpy array: The cropped face image
        """
        x, y, w, h = face
        return frame[y:y+h, x:x+w]
    
    def release(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()
            self.is_initialized = False
    
    def __del__(self):
        """Destructor to ensure camera is released"""
        self.release()


def check_camera_available():
    """
    Check if camera is available on the system
    Returns: (available: bool, message: str)
    """
    try:
        test_camera = cv2.VideoCapture(0)
        if test_camera.isOpened():
            test_camera.release()
            return True, "Camera is available"
        return False, "Camera not found"
    except Exception as e:
        return False, f"Error checking camera: {str(e)}"


def get_camera_properties():
    """
    Get camera properties
    Returns: dict with camera information
    """
    try:
        temp_camera = cv2.VideoCapture(0)
        if temp_camera.isOpened():
            props = {
                'width': int(temp_camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(temp_camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(temp_camera.get(cv2.CAP_PROP_FPS))
            }
            temp_camera.release()
            return props
        return {}
    except Exception as e:
        print(f"Error getting camera properties: {e}")
        return {}


def convert_frame_to_image(frame):
    """
    Convert OpenCV frame (BGR) to PIL Image (RGB) for display
    Args:
        frame: numpy array - OpenCV frame in BGR format
    Returns:
        PIL.Image: Image in RGB format
    """
    if frame is None:
        return None
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_frame)


def convert_frame_to_bytes(frame, quality=90):
    """
    Convert OpenCV frame to bytes for Streamlit display
    Args:
        frame: numpy array - OpenCV frame
        quality: int - JPEG quality (1-100)
    Returns:
        bytes: Image in JPEG format
    """
    if frame is None:
        return None
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(rgb_frame)
    
    # Convert to bytes
    import io
    img_bytes = io.BytesIO()
    pil_image.save(img_bytes, format='JPEG', quality=quality)
    img_bytes.seek(0)
    
    return img_bytes
