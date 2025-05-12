from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import qrcode
from io import BytesIO
import base64
import random
import os

app = FastAPI()
storage = {}  # {(qr_id, session_id): filename}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qr/guardar-foto")
def guardar_foto(
    qr_id: int = Form(...),
    session_id: str = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        filename = f"{qr_id}_{session_id}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(imagen.file.read())

        key = (qr_id, session_id)
        storage[key] = filename
        return {"status": "ok", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qr/verificar-foto")
def verificar_foto(qr_id: int = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    if key in storage:
        return {"imagen_url": f"https://foto-api-production.up.railway.app/qr/imagen/{storage[key]}"}
    return {"imagen_url": None}

@app.get("/qr/imagen/{filename}")
def get_image(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(filepath, media_type="image/jpeg")
