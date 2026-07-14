import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["kpis"])

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "kpis.json"


def load_data() -> dict:
    """Carga los datos de KPIs desde el archivo JSON.

    Reemplazar esta función por una consulta real al WMS / base de datos
    cuando haya una fuente de datos en producción.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/zones")
def get_zones():
    """Devuelve las zonas operativas y los KPIs que contiene cada una."""
    data = load_data()
    return data["zones"]


@router.get("/kpis")
def get_all_kpis():
    """Devuelve el detalle de todos los KPIs."""
    data = load_data()
    return data["kpis"]


@router.get("/kpis/{kpi_id}")
def get_kpi(kpi_id: str):
    """Devuelve el detalle de un KPI puntual."""
    data = load_data()
    kpi = data["kpis"].get(kpi_id)
    if kpi is None:
        raise HTTPException(status_code=404, detail=f"KPI '{kpi_id}' no encontrado")
    return kpi
