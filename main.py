from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import qrcode
from io import BytesIO
import base64
import random

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria
foto_storage = {}  # (qr_id, session_id): [imagenes]
qr_urls = {}       # qr_id: url generada

# ✅ MODELO DE ENTRADA PARA GENERAR QR
class QRRequest(BaseModel):
    session_id: str

@app.post("/qr/generador")
def generar_qr(request: QRRequest):
    try:
        qr_id = random.randint(100000, 999999)
        url = f"https://adrieldt911.github.io/FotoWeb/?qr_id={qr_id}&session_id={request.session_id}"

        # Generar imagen del QR
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        qr_urls[qr_id] = url

        return {
            "qr": base64.b64encode(qr_bytes).decode(),
            "url": url,
            "qr_id": qr_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando QR: {str(e)}")

# ✅ GUARDAR FOTOS MULTIPLES
@app.post("/qr/guardar-fotos")
async def guardar_fotos(
    qr_id: str = Form(...),
    session_id: str = Form(...),
    imagenes: List[UploadFile] = File(...)
):
    key = (qr_id, session_id)
    if key not in foto_storage:
        foto_storage[key] = []

    for image in imagenes:
        contents = await image.read()
        foto_storage[key].append(contents)

    return {
        "status": "ok",
        "message": f"{len(imagenes)} imagen(es) recibida(s) para QR_ID {qr_id}."
    }

# ✅ VERIFICAR CANTIDAD DE FOTOS SUBIDAS (para polling)
@app.get("/qr/verificar-fotos")
def verificar_fotos(qr_id: str = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    imagenes = foto_storage.get(key, [])
    return {
        "count": len(imagenes),
        "success": len(imagenes) > 0
    }
