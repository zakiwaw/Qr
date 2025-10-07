import os
import uuid
import base64
from datetime import datetime, timezone
from io import BytesIO
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
from qrcode.constants import ERROR_CORRECT_M

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


class QRCodeRequest(BaseModel):
    text: str


class QRCodeResponse(BaseModel):
    id: str
    text: str
    qrcode_image: str  # base64 encoded image
    created_at: str


class QRCodeListResponse(BaseModel):
    qrcodes: List[QRCodeResponse]

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


def generate_qrcode_image(text: str) -> str:
    """Generate QR code and return as base64 string."""
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=f"Error generating QR code: {str(exc)}") from exc

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

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Barcode Generator API", "status": "running"}

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


@app.post("/api/generate-qrcode", response_model=QRCodeResponse)
async def generate_qrcode(request: QRCodeRequest):
    """Generate a new QR code and save to database."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        qrcode_id = str(uuid.uuid4())
        qrcode_image = generate_qrcode_image(request.text.strip())
        qrcode_doc = {
            "id": qrcode_id,
            "text": request.text.strip(),
            "qrcode_image": qrcode_image,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.qrcodes.insert_one(prepare_for_mongo(qrcode_doc.copy()))
        return QRCodeResponse(**qrcode_doc)
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover - database failure
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")


@app.get("/api/qrcodes", response_model=QRCodeListResponse)
async def get_all_qrcodes():
    """Get all generated QR codes from database."""
    try:
        qrcodes = await db.qrcodes.find().sort("created_at", -1).to_list(length=None)
        qrcode_list = [parse_from_mongo(qrcode) for qrcode in qrcodes]
        return QRCodeListResponse(qrcodes=qrcode_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching QR codes: {str(e)}")


@app.get("/api/qrcode/{qrcode_id}", response_model=QRCodeResponse)
async def get_qrcode(qrcode_id: str):
    """Get specific QR code by ID."""
    try:
        qrcode_item = await db.qrcodes.find_one({"id": qrcode_id})
        if not qrcode_item:
            raise HTTPException(status_code=404, detail="QR code not found")
        return QRCodeResponse(**parse_from_mongo(qrcode_item))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching QR code: {str(e)}")


@app.delete("/api/qrcode/{qrcode_id}")
async def delete_qrcode(qrcode_id: str):
    """Delete specific QR code by ID."""
    try:
        result = await db.qrcodes.delete_one({"id": qrcode_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="QR code not found")
        return {"message": "QR code deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting QR code: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)