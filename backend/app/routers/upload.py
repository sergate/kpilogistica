"""
Router para manejar la carga de archivos y procesamiento de datos.
"""
import csv
import io
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import openpyxl

import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import (
    clear_all_data,
    insert_clientes,
    insert_pedidos_tienda,
    insert_pedidos_grupo,
    get_productividad_picking
)

router = APIRouter(prefix="/api", tags=["upload"])


def parse_excel_clientes(file_content: bytes) -> list[dict]:
    """
    Parsea el archivo Excel de clientes.
    Asume que tiene columnas: codigo, nombre, canal
    """
    wb = openpyxl.load_workbook(io.BytesIO(file_content))
    sheet = wb.active
    
    # Leer encabezados (primera fila)
    headers = [cell.value for cell in sheet[1]]
    
    # Leer datos
    data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0]:  # Si hay código
            record = dict(zip(headers, row))
            data.append({
                "codigo": record.get("codigo") or record.get("Codigo"),
                "nombre": record.get("nombre") or record.get("Nombre"),
                "canal": record.get("canal") or record.get("Canal")
            })
    
    return data


def parse_csv_pedidos(file_content: bytes, tipo: str) -> list[dict]:
    """
    Parsea archivos CSV con separador ; y comillas.
    tipo: 'tienda' o 'grupo'
    """
    content = file_content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(content), delimiter=';', quotechar='"')
    
    data = []
    for row in reader:
        if tipo == "tienda":
            data.append({
                "fecha": row.get("fecha") or row.get("Fecha"),
                "tienda": row.get("tienda") or row.get("Tienda"),
                "pedido_id": row.get("pedido_id") or row.get("Pedido"),
                "cantidad": int(row.get("cantidad", 0) or row.get("Cantidad", 0)),
                "operador": row.get("operador") or row.get("Operador"),
                "turno": row.get("turno") or row.get("Turno")
            })
        elif tipo == "grupo":
            data.append({
                "fecha": row.get("fecha") or row.get("Fecha"),
                "grupo": row.get("grupo") or row.get("Grupo"),
                "pedido_id": row.get("pedido_id") or row.get("Pedido"),
                "unidades": int(row.get("unidades", 0) or row.get("Unidades", 0)),
                "horas_trabajadas": float(row.get("horas_trabajadas", 0) or row.get("Horas", 0)),
                "categoria": row.get("categoria") or row.get("Categoria")
            })
    
    return data


@router.post("/upload-files")
async def upload_files(
    clientes: UploadFile = File(...),
    pedidos_tienda: UploadFile = File(...),
    pedidos_grupo: UploadFile = File(...)
):
    """
    Recibe los 3 archivos, borra datos anteriores y carga los nuevos.
    """
    try:
        # Leer archivos
        clientes_content = await clientes.read()
        pedidos_tienda_content = await pedidos_tienda.read()
        pedidos_grupo_content = await pedidos_grupo.read()
        
        # Validar extensiones
        if not clientes.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="El archivo de clientes debe ser .xlsx")
        
        if not pedidos_tienda.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="El archivo de pedidos por tienda debe ser .csv")
        
        if not pedidos_grupo.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="El archivo de pedidos por grupo debe ser .csv")
        
        # Parsear archivos
        clientes_data = parse_excel_clientes(clientes_content)
        pedidos_tienda_data = parse_csv_pedidos(pedidos_tienda_content, "tienda")
        pedidos_grupo_data = parse_csv_pedidos(pedidos_grupo_content, "grupo")
        
        # Borrar datos anteriores
        clear_all_data()
        
        # Insertar nuevos datos
        insert_clientes(clientes_data)
        insert_pedidos_tienda(pedidos_tienda_data)
        insert_pedidos_grupo(pedidos_grupo_data)
        
        # Calcular nueva productividad
        productividad = get_productividad_picking()
        
        return JSONResponse({
            "success": True,
            "message": "Datos procesados correctamente",
            "registros": {
                "clientes": len(clientes_data),
                "pedidos_tienda": len(pedidos_tienda_data),
                "pedidos_grupo": len(pedidos_grupo_data)
            },
            "productividad": productividad
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivos: {str(e)}")


@router.get("/picking-data")
def get_picking_data():
    """
    Retorna los datos de productividad de picking desde la base de datos.
    """
    try:
        data = get_productividad_picking()
        return JSONResponse(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@router.delete("/clear-data")
def clear_data():
    """
    Borra todos los datos de la base de datos.
    """
    try:
        clear_all_data()
        return JSONResponse({
            "success": True,
            "message": "Datos borrados correctamente"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar datos: {str(e)}")
