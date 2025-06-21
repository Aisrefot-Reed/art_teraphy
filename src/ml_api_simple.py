"""
Simplified ML API Process for Emotion Analysis (Testing Version)
This FastAPI application provides a mock emotion analysis for testing purposes.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Art Therapist ML API (Test Version)", description="Mock emotion analysis API for testing")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock emotions for testing
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Art Therapist ML API (Test Version) is running", "status": "healthy"}

@app.post("/analyze_emotion")
async def analyze_emotion(file: UploadFile = File(...)):
    """
    Mock emotion analysis from uploaded image
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Mock emotion analysis results
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data (just to validate it's a real image)
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Mock emotion detection - randomly select an emotion for testing
        dominant_emotion = random.choice(EMOTIONS)
        
        # Create mock emotion scores
        emotions = {}
        for emotion in EMOTIONS:
            if emotion == dominant_emotion:
                emotions[emotion] = random.uniform(0.6, 0.9)  # High confidence for dominant
            else:
                emotions[emotion] = random.uniform(0.0, 0.3)  # Low confidence for others
        
        # Normalize to sum to 1
        total = sum(emotions.values())
        emotions = {k: v/total for k, v in emotions.items()}
        
        return {
            "status": "success",
            "dominant_emotion": dominant_emotion,
            "emotions": emotions,
            "confidence": emotions[dominant_emotion]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/health")
async def health_check():
    """Extended health check with model status"""
    return {
        "status": "healthy",
        "model_loaded": True,
        "message": "Mock ML API is ready to process images",
        "note": "This is a test version with mock emotion detection"
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "ml_api_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

