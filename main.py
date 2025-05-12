from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import qrcode
from io import BytesIO
import base64
import random
from PIL import Image
import io

app = FastAPI()

# Almacén de imágenes: {(qr_id, session_id): base64_image_string}
image_storage = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---

class QRRequest(BaseModel):
    session_id: str

# --- ENDPOINT PARA GENERAR QR ---

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

# --- ENDPOINT PARA GUARDAR IMAGEN ---

@app.post("/qr/guardar-imagen")
async def guardar_imagen(
    qr_id: int = Form(...),
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        # Convertir a imagen para verificar que sea válida
        image = Image.open(io.BytesIO(contents))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode()

        key = (qr_id, session_id.strip())
        image_storage[key] = base64_image

        print(f"✅ Imagen recibida para: {key}")

        return {"status": "ok", "message": f"Imagen guardada para QR_ID {qr_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")

# --- ENDPOINT PARA VERIFICAR SI LA IMAGEN FUE ENVIADA ---

@app.get("/qr/verificar-imagen")
def verificar_imagen(qr_id: int = Query(...), session_id: str = Query(...)):
    try:
        key = (qr_id, session_id.strip())
        base64_image = image_storage.get(key)
        if base64_image:
            return {"image": base64_image}
        return {"image": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando imagen: {str(e)}")
