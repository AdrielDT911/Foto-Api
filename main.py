from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI()

# Directorio donde se guardarán las imágenes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Almacenamiento en memoria: {(qr_id, session_id): filename}
image_storage = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/qr/generar")
def generar_qr(session_id: str = Form(...)):
    import qrcode
    from io import BytesIO
    import base64
    import random

    qr_id = random.randint(1, 999999)
    url = f"https://adrieldt911.github.io/FotoWeb/?qr_id={qr_id}&session_id={session_id}"

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_bytes = buffer.getvalue()

    return {
        "qr": base64.b64encode(qr_bytes).decode(),
        "qr_id": qr_id,
        "url": url
    }

@app.post("/qr/guardar-imagen")
async def guardar_imagen(
    qr_id: int = Form(...),
    session_id: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(await image.read())

        key = (qr_id, session_id)
        image_storage[key] = filename

        return {"status": "ok", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qr/verificar-imagen")
def verificar_imagen(qr_id: int = Query(...), session_id: str = Query(...)):
    key = (qr_id, session_id)
    if key in image_storage:
        return {"image_url": f"/qr/imagen?filename={image_storage[key]}"}
    return {"image_url": None}

@app.get("/qr/imagen")
def mostrar_imagen(filename: str = Query(...)):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Imagen no encontrada")
