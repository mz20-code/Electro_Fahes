"""
Electro_Fahes - AI Model for Inverter Diagnostics
This module handles image analysis and error detection
"""

import os
import json
from PIL import Image
import numpy as np

# ============================================================================
# Error Code Database
# ============================================================================

ERROR_DATABASE = {
    "07": {
        "name": "Grid Overvoltage",
        "description": "The grid voltage exceeds the acceptable range",
        "severity": "high",
        "solutions": [
            "Check grid voltage with multimeter",
            "Verify voltage protection settings in inverter",
            "Contact grid operator if voltage persistently high",
            "Consider installing voltage regulator"
        ]
    },
    "10": {
        "name": "Grid Fault",
        "description": "Grid connection issue detected",
        "severity": "high",
        "solutions": [
            "Check all AC connections and cables",
            "Verify circuit breaker status",
            "Test grid voltage and frequency",
            "Inspect for loose connections"
        ]
    },
    "24": {
        "name": "Grid Undervoltage",
        "description": "Grid voltage is below acceptable range",
        "severity": "medium",
        "solutions": [
            "Measure actual grid voltage",
            "Check for voltage drops in main distribution",
            "Verify cable sizing is adequate",
            "Contact electricity provider"
        ]
    },
    "29": {
        "name": "Isolation Fault",
        "description": "PV array isolation resistance too low",
        "severity": "high",
        "solutions": [
            "Check for water ingress in junction boxes",
            "Inspect PV cables for damage",
            "Test isolation resistance with megger",
            "Check for ground faults in array"
        ]
    },
    "pv_fault": {
        "name": "PV Input Fault",
        "description": "Problem with solar panel input",
        "severity": "medium",
        "solutions": [
            "Check PV string voltage",
            "Verify PV connections and cables",
            "Inspect for shading or panel damage",
            "Test individual panel voltages"
        ]
    },
    "temperature": {
        "name": "Temperature Warning",
        "description": "Inverter temperature too high",
        "severity": "medium",
        "solutions": [
            "Ensure adequate ventilation",
            "Clean cooling vents and fans",
            "Check ambient temperature",
            "Verify inverter not in direct sunlight"
        ]
    }
}

# ============================================================================
# AI Model Class
# ============================================================================

class InverterDiagnosticModel:
    """
    AI model for analyzing inverter images and detecting errors
    TODO: Replace with actual trained deep learning model
    """
    
    def __init__(self):
        self.error_db = ERROR_DATABASE
        self.model_loaded = False
        
    def load_model(self):
        """
        Load the trained model
        In production, this would load a TensorFlow/PyTorch model
        """
        # TODO: Load actual trained model
        # self.model = tf.keras.models.load_model('path/to/model.h5')
        self.model_loaded = True
        
    def preprocess_image(self, image_path):
        """
        Preprocess image for model input
        """
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((224, 224))  # Standard input size
            img_array = np.array(img) / 255.0
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def detect_error_code(self, image_path):
        """
        Detect error code from image
        TODO: Implement actual OCR/computer vision detection
        """
        # Placeholder: Random error detection for demo
        # In production, use OCR (Tesseract) or trained CNN
        import random
        error_codes = list(self.error_db.keys())
        detected_code = random.choice(error_codes)
        confidence = random.uniform(0.75, 0.95)
        
        return detected_code, confidence
    
    def generate_diagnosis(self, error_code, model_name="Unknown", confidence=0.85):
        """
        Generate detailed diagnosis report
        """
        if error_code not in self.error_db:
            return self._generate_generic_diagnosis(model_name)
        
        error_info = self.error_db[error_code]
        
        diagnosis = f"""
        <div class="diagnosis-report">
            <div class="diagnosis-header">
                <span class="severity-badge {error_info['severity']}">{error_info['severity'].upper()}</span>
                <h3>Error Detected: {error_info['name']}</h3>
            </div>
            
            <div class="diagnosis-section">
                <h4>Description:</h4>
                <p>{error_info['description']}</p>
            </div>
            
            <div class="diagnosis-section">
                <h4>Confidence Level:</h4>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence*100}%"></div>
                </div>
                <p>{confidence*100:.1f}% confident in this diagnosis</p>
            </div>
            
            <div class="diagnosis-section">
                <h4>Recommended Solutions:</h4>
                <ol class="solution-list">
                    {''.join([f'<li>{solution}</li>' for solution in error_info['solutions']])}
                </ol>
            </div>
            
            <div class="diagnosis-section">
                <h4>⚠️ Safety Note:</h4>
                <p>If you're unsure about any repairs, please contact a certified technician. Working with high voltage can be dangerous.</p>
            </div>
        </div>
        """
        
        return diagnosis
    
    def _generate_generic_diagnosis(self, model_name):
        """
        Generate generic diagnosis when specific error not detected
        """
        return f"""
        <div class="diagnosis-report">
            <h3>Analysis Complete</h3>
            <p>Model: {model_name}</p>
            <p>Unable to detect a specific error code from the image. This could mean:</p>
            <ul>
                <li>The inverter is functioning normally</li>
                <li>The error screen is not clearly visible</li>
                <li>The error type is not in our database yet</li>
            </ul>
            <p><strong>Recommendations:</strong></p>
            <ol>
                <li>Try uploading a clearer image of the error display</li>
                <li>Check inverter manual for error code reference</li>
                <li>Contact our technicians for in-person diagnosis</li>
            </ol>
        </div>
        """

# ============================================================================
# Public API Functions
# ============================================================================

_model_instance = None

def get_model():
    """Get or create model instance (singleton)"""
    global _model_instance
    if _model_instance is None:
        _model_instance = InverterDiagnosticModel()
        _model_instance.load_model()
    return _model_instance

def analyze_inverter_image(image_path, model_name="Unknown"):
    """
    Main function to analyze inverter image
    
    Args:
        image_path: Path to uploaded image
        model_name: Inverter model name (optional)
    
    Returns:
        HTML formatted diagnosis report
    """
    model = get_model()
    
    # Preprocess image
    img_array = model.preprocess_image(image_path)
    if img_array is None:
        return "Error: Unable to process image. Please upload a valid image file."
    
    # Detect error code
    error_code, confidence = model.detect_error_code(image_path)
    
    # Generate diagnosis
    diagnosis = model.generate_diagnosis(error_code, model_name, confidence)
    
    return diagnosis

def get_error_info(error_code):
    """
    Get information about specific error code
    """
    model = get_model()
    return model.error_db.get(error_code, None)

# ============================================================================
# Utility Functions
# ============================================================================

def save_error_database(filepath='data/inverter_errors.json'):
    """
    Save error database to JSON file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(ERROR_DATABASE, f, indent=2)

def load_error_database(filepath='data/inverter_errors.json'):
    """
    Load error database from JSON file
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return ERROR_DATABASE

# Initialize error database on module import
if __name__ == '__main__':
    save_error_database()
    print("Error database saved successfully!")