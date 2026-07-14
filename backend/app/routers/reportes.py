"""
Router para manejar reportes de Status Preparación.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import get_connection, init_database

router = APIRouter(prefix="/api/reportes", tags=["reportes"])


@router.get("/resumen")
def get_resumen():
    """
    Retorna un resumen general de todos los datos importados.
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) as total FROM clientes")
        total_clientes = cursor.fetchone()["total"]
        
        # Total de pedidos por tienda
        cursor.execute("SELECT COUNT(*) as total, SUM(cantidad) as unidades FROM pedidos_tienda")
        pedidos_tienda = cursor.fetchone()
        
        # Total de pedidos por grupo
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                SUM(unidades) as total_unidades,
                SUM(horas_trabajadas) as total_horas,
                ROUND(SUM(unidades) * 1.0 / NULLIF(SUM(horas_trabajadas), 0), 2) as productividad
            FROM pedidos_grupo
        """)
        pedidos_grupo = cursor.fetchone()
        
        # Clientes por canal
        cursor.execute("""
            SELECT canal, COUNT(*) as cantidad 
            FROM clientes 
            GROUP BY canal
        """)
        clientes_canal = [{"canal": row["canal"], "cantidad": row["cantidad"]} 
                          for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "resumen": {
                "clientes": {
                    "total": total_clientes,
                    "por_canal": clientes_canal
                },
                "pedidos_tienda": {
                    "total": pedidos_tienda["total"] if pedidos_tienda else 0,
                    "unidades": pedidos_tienda["unidades"] if pedidos_tienda else 0
                },
                "pedidos_grupo": {
                    "total": pedidos_grupo["total_pedidos"] if pedidos_grupo else 0,
                    "unidades": pedidos_grupo["total_unidades"] if pedidos_grupo else 0,
                    "horas": pedidos_grupo["total_horas"] if pedidos_grupo else 0,
                    "productividad": pedidos_grupo["productividad"] if pedidos_grupo else 0
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "No hay datos cargados. Importa archivos primero."
        }


@router.get("/por-fecha")
def get_por_fecha():
    """
    Retorna datos agrupados por fecha.
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                fecha,
                COUNT(*) as cantidad_pedidos,
                SUM(unidades) as total_unidades,
                SUM(horas_trabajadas) as total_horas,
                ROUND(SUM(unidades) * 1.0 / NULLIF(SUM(horas_trabajadas), 0), 2) as productividad,
                GROUP_CONCAT(DISTINCT categoria) as categorias
            FROM pedidos_grupo
            GROUP BY fecha
            ORDER BY fecha DESC
        """)
        
        datos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "datos": datos,
            "total_registros": len(datos)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "No hay datos cargados. Importa archivos primero."
        }


@router.get("/por-marca")
def get_por_marca():
    """
    Retorna datos agrupados por marca (derivado del grupo o tienda).
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        # Asumimos que los grupos o tiendas pueden indicar marca
        cursor.execute("""
            SELECT 
                grupo as marca,
                COUNT(*) as cantidad_pedidos,
                SUM(unidades) as total_unidades,
                SUM(horas_trabajadas) as total_horas,
                ROUND(SUM(unidades) * 1.0 / NULLIF(SUM(horas_trabajadas), 0), 2) as productividad
            FROM pedidos_grupo
            GROUP BY grupo
            ORDER BY total_unidades DESC
        """)
        
        datos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "datos": datos,
            "total_marcas": len(datos)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "No hay datos cargados. Importa archivos primero."
        }


@router.get("/por-canal")
def get_por_canal():
    """
    Retorna datos agrupados por canal de distribución.
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.canal,
                COUNT(DISTINCT pt.pedido_id) as cantidad_pedidos,
                SUM(pt.cantidad) as total_unidades
            FROM clientes c
            LEFT JOIN pedidos_tienda pt ON 1=1
            WHERE c.canal IS NOT NULL
            GROUP BY c.canal
            ORDER BY total_unidades DESC
        """)
        
        datos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "datos": datos,
            "total_canales": len(datos)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "No hay datos cargados. Importa archivos primero."
        }


@router.get("/por-categoria")
def get_por_categoria():
    """
    Retorna datos agrupados por categoría de producto.
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as cantidad_pedidos,
                SUM(unidades) as total_unidades,
                SUM(horas_trabajadas) as total_horas,
                ROUND(SUM(unidades) * 1.0 / NULLIF(SUM(horas_trabajadas), 0), 2) as productividad
            FROM pedidos_grupo
            WHERE categoria IS NOT NULL
            GROUP BY categoria
            ORDER BY total_unidades DESC
        """)
        
        datos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "datos": datos,
            "total_categorias": len(datos)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "No hay datos cargados. Importa archivos primero."
        }
