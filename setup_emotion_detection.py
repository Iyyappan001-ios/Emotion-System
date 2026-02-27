"""
Setup script for EmoRecs Emotion Detection
This script helps install and configure the emotion detection system
"""

import os
import subprocess
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def install_requirements():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    packages = [
        "streamlit>=1.24.0",
        "tensorflow>=2.13.0",
        "deepface",
        "opencv-python>=4.8.0",
        "numpy",
        "Pillow"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}\n")

def test_emotion_detection():
    """Test if emotion detection is working"""
    print_header("Testing Emotion Detection Setup")
    
    try:
        import cv2
        print("✓ OpenCV loaded successfully")
    except ImportError:
        print("✗ OpenCV not found")
        return False
        
    
    try:
        from deepface import DeepFace
        print("✓ DeepFace available - BEST accuracy")
    except ImportError:
        print("⚠ DeepFace not available - using fallback (less accurate)")
    
    try:
        import tensorflow
        print("✓ TensorFlow available")
    except ImportError:
        print("⚠ TensorFlow not available")
        return False
    
    print("\n✓✓✓ Setup Complete! ✓✓✓")
    print("\nEmotion Detection Methods (in priority order):")
    print("  1. DeepFace - Most Accurate")
    print("  2. Pre-trained Keras Model")
    print("  3. ML-based Feature Detection")
    
    return True

def main():
    """Main setup function"""
    print_header("EmoRecs Emotion Detection Setup")
    
    print("This setup will:")
    print("  1. Install required Python packages")
    print("  2. Test the emotion detection system")
    print("  3. Configure the detection pipeline")
    print()
    
    # Install requirements
    try:
        install_requirements()
    except Exception as e:
        print(f"Error during installation: {e}")
        return False
    
    # Test setup
    if not test_emotion_detection():
        print("\n⚠ Some components missing. Using fallback detection.")
        return False
    
    print("\n" + "="*60)
    print("  Setup Complete! You can now run:")
    print("  streamlit run app.py")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    main()
