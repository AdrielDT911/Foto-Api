from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import base64
import qrcode
from io import BytesIO
import random

app = FastAPI()

foto_storage = {}  # {(qr_id, session_id): [base64_foto1, base64_foto2, ...]}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRRequest(BaseModel):
    session_id: str

class FotoRequest(BaseModel):
    qr_id: int
    session_id: str
    foto_base64: str

@app.post("/qr/generador")
def generar_qr(request: QRRequest):
    try:
        qr_id = random.randint(100000, 999999)
        qr_url = f"https://adrieldt911.github.io/FotoWeb/?qr_id={qr_id}&session_id={request.session_id}"
        qr = qrcode.make(qr_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()
        return {
            "qr": base64.b64encode(qr_bytes).decode(),
            "qr_id": qr_id,
            "url": qr_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qr/subir-foto")
def subir_foto(req: FotoRequest):
    key = (req.qr_id, req.session_id)
    if key not in foto_storage:
        foto_storage[key] = []
    foto_storage[key].append(req.foto_base64)
    return {"success": True, "message": "Foto guardada"}

@app.get("/qr/obtener-fotos")
def obtener_fotos(qr_id: int = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    return {
        "success": True,
        "images": foto_storage.get(key, [])
    }
