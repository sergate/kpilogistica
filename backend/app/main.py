import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Aseguramos que "backend/" esté en sys.path para que el import de abajo
# funcione sin importar cómo se invoque este archivo (uvicorn local o el
# runtime de Vercel, que puede ejecutar el entrypoint con un cwd distinto).
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.routers import kpis, upload, reportes  # noqa: E402

app = FastAPI(
    title="KPI Logística API",
    description="API de indicadores operativos del depósito",
    version="1.0.0",
)

# En desarrollo permitimos cualquier origen. Restringir en producción
# a los dominios reales del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kpis.router)
app.include_router(upload.router)
app.include_router(reportes.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
