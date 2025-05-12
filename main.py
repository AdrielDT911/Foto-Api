from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import qrcode
from io import BytesIO
import base64
import random

app = FastAPI()
foto_storage = {}  # Estructura: {(qr_id, session_id): image_base64}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 MODELOS
class QRRequest(BaseModel):
    session_id: str

class FotoRequest(BaseModel):
    qr_id: int
    session_id: str
    image_base64: str  # imagen en base64

# 📌 GENERADOR DE QR
@app.post("/qr/generador")
def generar_qr(request: QRRequest):
    try:
        qr_id = random.randint(100000, 999999)
        qr_data = f"https://adrieldt911.github.io/FotoWeb/?qr_id={qr_id}&session_id={request.session_id}"

        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        return {
            "qr": base64.b64encode(qr_bytes).decode(),
            "url": qr_data,
            "qr_id": qr_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando QR: {str(e)}")

# 📌 GUARDAR FOTO EN BASE64
@app.post("/foto/guardar")
def guardar_foto(request: FotoRequest):
    try:
        key = (request.qr_id, request.session_id)
        foto_storage[key] = request.image_base64
        return {"status": "ok", "message": "Foto recibida y almacenada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando foto: {str(e)}")

# 📌 VERIFICAR FOTO POR POLLING
@app.get("/foto/verificar")
def verificar_foto(qr_id: int = Query(...), session_id: str = Query(...)):
    try:
        key = (qr_id, session_id)
        return {"image_base64": foto_storage.get(key)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar foto: {str(e)}")
