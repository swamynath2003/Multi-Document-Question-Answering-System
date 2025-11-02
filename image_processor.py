import os
import re
import subprocess
import pytesseract
from PIL import Image
import streamlit as st

class TesseractManager:
    """Manages Tesseract OCR installation and configuration"""
    def __init__(self):
        self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def is_available(self):
        """Check if Tesseract OCR is installed and available"""
        if not os.path.isfile(self.tesseract_cmd):
            return False
        try:
            subprocess.run([self.tesseract_cmd, '--version'], capture_output=True, check=True)
            return True
        except:
            return False

    def configure_tesseract(self):
        """Configure the pytesseract library to use the installed Tesseract OCR"""
        if not self.is_available():
            raise EnvironmentError("Tesseract OCR not found")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

class ImageProcessor:
    """Process images to extract text using OCR"""
    def __init__(self):
        try:
            self.tesseract_manager = TesseractManager()
            if not self.tesseract_manager.is_available():
                st.warning("Tesseract OCR is not installed. Image processing functionality will be limited.")
            else:
                self.tesseract_manager.configure_tesseract()
        except Exception as e:
            st.warning(f"Image processing setup error: {str(e)}")
        
    def process_image(self, image):
        """Extract text from an image using OCR"""
        try:
            img = image.convert('L')  # Convert to grayscale for better OCR
            text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
            return self.clean_text(text)
        except Exception as e:
            st.error(f"OCR Error: {str(e)}")
            return ""
    
    def clean_text(self, text):
        """Clean the extracted text"""
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        text = re.sub(r'\s+', ' ', text).strip()     # Normalize whitespace
        return text