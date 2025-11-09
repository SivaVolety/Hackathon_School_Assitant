from fastapi import FastAPI
from pydantic import BaseModel
import logging
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- FastAPI App --------------------
app = FastAPI(title="School Assistant API")

class AbsenceRequest(BaseModel):
    date: str
    reason: str

@app.post("/tools/report_absence")
async def report_absence_endpoint(request: AbsenceRequest):
    """REST endpoint for reporting absence"""
    try:
        logger.info(f"Absence reported for {request.date}: {request.reason}")
        return {
            "success": True,
            "message": f"✅ Absence successfully reported for {request.date}. Reason: {request.reason}"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "success": False,
            "message": f"❌ Error: {str(e)}"
        }

@app.get("/tools/get_lunch_menu")
async def get_lunch_menu_endpoint():
    """REST endpoint for getting lunch menu"""
    try:
        today = date.today().strftime('%B %d, %Y')
        return {
            "success": True,
            "menu": f"🍽️ Today's Lunch Menu ({today})\n\n🍕 Pizza\n🥗 Caesar Salad\n🍎 Fresh Fruit\n🥛 Milk\n🍪 Cookies"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "success": False,
            "menu": f"❌ Error: {str(e)}"
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "School Assistant API is running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# -------------------- Run Server --------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting School Assistant API Server...")
    logger.info("📝 Server will be available at http://127.0.0.1:8000")
    logger.info("📚 API docs at http://127.0.0.1:8000/docs")
    logger.info("🛑 Press CTRL+C to quit")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")