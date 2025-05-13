from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import qrcode
from io import BytesIO
import base64
import random
import os

app = FastAPI()

# Diccionario para registrar imágenes por sesión
foto_storage = {}  # {(qr_id, session_id): [filename1, filename2, ...]}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRRequest(BaseModel):
    session_id: str

@app.post("/qr/generador")
def generar_qr(request: QRRequest):
    try:
        qr_id = random.randint(1, 999999)
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

@app.post("/qr/guardar-foto")
async def guardar_foto(
    imagenes: List[UploadFile] = File(...),
    qr_id: int = Form(...),
    session_id: str = Form(...)
):
    try:
        os.makedirs("fotos", exist_ok=True)
        key = (qr_id, session_id)
        foto_storage[key] = []

        for idx, img in enumerate(imagenes):
            filename = f"{qr_id}_{session_id}_{idx}.jpg"
            path = os.path.join("fotos", filename)

            with open(path, "wb") as f:
                f.write(await img.read())

            foto_storage[key].append(filename)

        return {"status": "ok", "fotos": foto_storage[key]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando imagen: {str(e)}")

@app.get("/qr/verificar-foto")
def verificar_foto(qr_id: int = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    fotos = foto_storage.get(key, [])
    return {"imagenes": fotos}
