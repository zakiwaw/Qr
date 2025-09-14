import os
import uuid
import base64
from datetime import datetime, timezone
from io import BytesIO
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from barcode import Code128
from barcode.writer import ImageWriter

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'barcode_generator')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# FastAPI app
app = FastAPI(title="Barcode Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (built React app)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Pydantic models
class BarcodeRequest(BaseModel):
    text: str

class BarcodeResponse(BaseModel):
    id: str
    text: str
    barcode_image: str  # base64 encoded image
    created_at: str

class BarcodeListResponse(BaseModel):
    barcodes: List[BarcodeResponse]

# Helper functions
def generate_barcode_image(text: str) -> str:
    """Generate Code128 barcode and return as base64 string"""
    try:
        # Create Code128 barcode
        code = Code128(text, writer=ImageWriter())
        
        # Generate image in memory
        buffer = BytesIO()
        code.write(buffer)
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating barcode: {str(e)}")

def prepare_for_mongo(data):
    """Prepare data for MongoDB storage"""
    if isinstance(data.get('created_at'), str):
        return data
    data['created_at'] = data['created_at'].isoformat() if 'created_at' in data else datetime.now(timezone.utc).isoformat()
    return data

def parse_from_mongo(item):
    """Parse data from MongoDB"""
    if isinstance(item.get('created_at'), str):
        return item
    return item

# Serve React app for all non-API routes
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the React frontend"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"message": "Frontend not built. Please build the React app first."}

# Catch all route for React Router (SPA)
@app.get("/{path:path}", include_in_schema=False)
async def serve_frontend_routes(path: str):
    """Serve React app for all frontend routes"""
    # Skip API routes
    if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc"):
        raise HTTPException(status_code=404, detail="Not found")
    
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"message": "Frontend not built"}

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"message": "Barcode Generator API", "status": "running", "frontend": os.path.exists("static/index.html")}

@app.post("/api/generate-barcode", response_model=BarcodeResponse)
async def generate_barcode(request: BarcodeRequest):
    """Generate a new barcode and save to database"""
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Generate unique ID
        barcode_id = str(uuid.uuid4())
        
        # Generate barcode image
        barcode_image = generate_barcode_image(request.text.strip())
        
        # Create barcode document
        barcode_doc = {
            "id": barcode_id,
            "text": request.text.strip(),
            "barcode_image": barcode_image,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database
        await db.barcodes.insert_one(prepare_for_mongo(barcode_doc.copy()))
        
        return BarcodeResponse(**barcode_doc)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating barcode: {str(e)}")

@app.get("/api/barcodes", response_model=BarcodeListResponse)
async def get_all_barcodes():
    """Get all generated barcodes from database"""
    try:
        barcodes = await db.barcodes.find().sort("created_at", -1).to_list(length=None)
        barcode_list = [parse_from_mongo(barcode) for barcode in barcodes]
        return BarcodeListResponse(barcodes=barcode_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching barcodes: {str(e)}")

@app.get("/api/barcode/{barcode_id}", response_model=BarcodeResponse)
async def get_barcode(barcode_id: str):
    """Get specific barcode by ID"""
    try:
        barcode = await db.barcodes.find_one({"id": barcode_id})
        if not barcode:
            raise HTTPException(status_code=404, detail="Barcode not found")
        return BarcodeResponse(**parse_from_mongo(barcode))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching barcode: {str(e)}")

@app.delete("/api/barcode/{barcode_id}")
async def delete_barcode(barcode_id: str):
    """Delete specific barcode by ID"""
    try:
        result = await db.barcodes.delete_one({"id": barcode_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Barcode not found")
        return {"message": "Barcode deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting barcode: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)