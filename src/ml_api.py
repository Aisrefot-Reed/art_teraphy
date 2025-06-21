"""
ML API Process for Emotion Analysis
This FastAPI application provides emotion analysis for images using the FER library.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from fer import FER
import io
from PIL import Image
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Art Therapist ML API", description="Emotion analysis API for art therapy bot")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize emotion detector
emotion_detector = FER(mtcnn=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Art Therapist ML API is running", "status": "healthy"}

@app.post("/analyze_emotion")
async def analyze_emotion(file: UploadFile = File(...)):
    """
    Analyze emotion from uploaded image
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Emotion analysis results
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert PIL image to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Analyze emotions
        emotions = emotion_detector.detect_emotions(opencv_image)
        
        if not emotions:
            return {
                "status": "no_face_detected",
                "message": "No face detected in the image",
                "dominant_emotion": "neutral",
                "emotions": {}
            }
        
        # Get the first detected face (assuming single person)
        face_emotions = emotions[0]['emotions']
        
        # Find dominant emotion
        dominant_emotion = max(face_emotions, key=face_emotions.get)
        
        return {
            "status": "success",
            "dominant_emotion": dominant_emotion,
            "emotions": face_emotions,
            "confidence": face_emotions[dominant_emotion]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/health")
async def health_check():
    """Extended health check with model status"""
    try:
        # Test if emotion detector is working
        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        emotion_detector.detect_emotions(test_array)
        
        return {
            "status": "healthy",
            "model_loaded": True,
            "message": "ML API is ready to process images"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "ml_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

