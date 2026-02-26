"""
Camera Detection Module for EmoRecs
Handles camera initialization, frame capture, and face detection using OpenCV
"""

import cv2
import numpy as np
from PIL import Image
import streamlit as st
import time


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
        Process a frame to detect faces and draw bounding boxes
        Args:
            frame: numpy array - the image frame in BGR format
        Returns:
            tuple: (processed_frame, detected_faces)
        """
        # Make a copy to avoid modifying original
        output_frame = frame.copy()
        
        # Detect faces
        faces = self.detect_faces(output_frame)
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), 
                         (0, 255, 0), 2)
            
            # Draw label
            cv2.putText(output_frame, 'Face', (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Optionally detect eyes within the face
            if self.eye_cascade is not None:
                roi_gray = frame[y:y+h, x:x+w]
                eyes = self.detect_eyes(roi_gray)
                
                for (ex, ey, ew, eh) in eyes[:2]:  # Limit to 2 eyes
                    cv2.rectangle(output_frame, 
                                 (x + ex, y + ey), 
                                 (x + ex + ew, y + ey + eh),
                                 (255, 0, 0), 1)
        
        return output_frame, faces
    
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
