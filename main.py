from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import base64

app = FastAPI()

# Almacenamiento temporal
foto_storage: Dict[tuple, str] = {}  # {(qr_id, session_id): base64_image}

# CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto si necesitas restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FotoRequest(BaseModel):
    qr_id: int
    session_id: str
    imagen: str  # Base64

@app.post("/qr/guardar-foto")
def guardar_foto(request: FotoRequest):
    try:
        key = (request.qr_id, request.session_id)
        foto_storage[key] = request.imagen
        return {"status": "ok", "message": "Imagen guardada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar imagen: {str(e)}")

@app.get("/qr/verificar-foto")
def verificar_foto(qr_id: int = Query(...), session_id: str = Query(...)):
    try:
        key = (qr_id, session_id)
        return {"imagen": foto_storage.get(key)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar imagen: {str(e)}")
