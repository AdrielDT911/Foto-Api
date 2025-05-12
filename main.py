# camera_api.py
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import qrcode
from io import BytesIO
import base64
import random
import os

app = FastAPI()
image_storage = {}  # {(qr_id, session_id): image_data_base64}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/qr/generador")
def generar_qr(session_id: str):
    qr_id = random.randint(100000, 999999)
    url = f"https://adrieldt911.github.io/FotoWeb/?qr_id={qr_id}&session_id={session_id}"

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_bytes = buffer.getvalue()

    return {
        "qr": base64.b64encode(qr_bytes).decode(),
        "url": url,
        "qr_id": qr_id
    }

@app.post("/qr/guardar-imagen")
async def guardar_imagen(
    qr_id: int = Query(...),
    session_id: str = Query(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    base64_image = base64.b64encode(content).decode()
    image_storage[(qr_id, session_id)] = base64_image
    return {"status": "ok", "message": "Imagen recibida."}

@app.get("/qr/verificar-imagen")
def verificar_imagen(qr_id: int = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    img_data = image_storage.get(key)
    return {"image": img_data}
