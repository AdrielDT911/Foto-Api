from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import qrcode
from io import BytesIO
import base64
import random
from PIL import Image
import io

app = FastAPI()
cdc_storage = {}  # Estructura: {(qr_id, session_id): image_data}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRRequest(BaseModel):
    session_id: str

class ImageRequest(BaseModel):
    qr_id: int
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

@app.post("/qr/guardar-imagen")
def guardar_imagen(request: ImageRequest, file: UploadFile = File(...)):
    try:
        # Guardar la imagen recibida
        image = Image.open(io.BytesIO(file.file.read()))
        image_data = image.tobytes()  # Este es un ejemplo. Se puede hacer el procesamiento que desees aquí.

        key = (request.qr_id, request.session_id)
        cdc_storage[key] = image_data

        return {"status": "ok", "message": f"Imagen recibida y guardada para QR_ID {request.qr_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")

@app.get("/qr/verificar-imagen")
def verificar_imagen(qr_id: int = Query(...), session_id: str = Query(...)):
    try:
        key = (qr_id, session_id)
        image_data = cdc_storage.get(key)
        if image_data:
            # Devolver la imagen en base64 (o el formato que necesites)
            image = Image.frombytes(image_data)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            return {"image": base64.b64encode(buffer.getvalue()).decode()}
        else:
            return {"image": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando la imagen: {str(e)}")
