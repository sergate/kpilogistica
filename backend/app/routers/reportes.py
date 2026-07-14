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
    Retorna un resumen general con:
    - Total Unidades (suma del campo Uni)
    - Unidades Pickeadas (suma del campo Uni.Pick)
    - Unidades Separadas (suma del campo Uni.Sep)
    - Pendiente Picking (diferencia entre Total y Pickeadas)
    - Pendiente Separación (diferencia entre Total y Separadas)
    - Efic. Picking (% pickeadas/total)
    - Efic. Separación (% separadas/total)
    - Total Registros
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        # Calcular totales del archivo grupos
        cursor.execute("""
            SELECT 
                COUNT(*) as total_registros,
                COALESCE(SUM(uni), 0) as total_unidades,
                COALESCE(SUM(uni_pick), 0) as unidades_pickeadas,
                COALESCE(SUM(uni_sep), 0) as unidades_separadas
            FROM pedidos_grupo
        """)
        resultado = cursor.fetchone()
        
        conn.close()
        
        total_unidades = resultado["total_unidades"]
        unidades_pickeadas = resultado["unidades_pickeadas"]
        unidades_separadas = resultado["unidades_separadas"]
        total_registros = resultado["total_registros"]
        
        # Calcular pendientes
        pendiente_picking = total_unidades - unidades_pickeadas
        pendiente_separacion = total_unidades - unidades_separadas
        
        # Calcular eficiencias
        efic_picking = round((unidades_pickeadas / total_unidades * 100), 2) if total_unidades > 0 else 0
        efic_separacion = round((unidades_separadas / total_unidades * 100), 2) if total_unidades > 0 else 0
        
        return {
            "success": True,
            "resumen": {
                "total_unidades": total_unidades,
                "unidades_pickeadas": unidades_pickeadas,
                "unidades_separadas": unidades_separadas,
                "pendiente_picking": pendiente_picking,
                "pendiente_separacion": pendiente_separacion,
                "efic_picking": efic_picking,
                "efic_separacion": efic_separacion,
                "total_registros": total_registros
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
    Retorna detalle por fecha y marca con:
    - fecha (orden descendente)
    - marca
    - unidades
    - pickeadas
    - separadas
    - Efic. Picking
    - Efic. Separación
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                fecha,
                marca,
                COALESCE(SUM(uni), 0) as unidades,
                COALESCE(SUM(uni_pick), 0) as pickeadas,
                COALESCE(SUM(uni_sep), 0) as separadas,
                CASE 
                    WHEN SUM(uni) > 0 THEN ROUND(SUM(uni_pick) * 100.0 / SUM(uni), 2)
                    ELSE 0 
                END as efic_picking,
                CASE 
                    WHEN SUM(uni) > 0 THEN ROUND(SUM(uni_sep) * 100.0 / SUM(uni), 2)
                    ELSE 0 
                END as efic_separacion
            FROM pedidos_grupo
            WHERE marca IS NOT NULL
            GROUP BY fecha, marca
            ORDER BY fecha DESC, marca
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
    Retorna datos agrupados por marca con:
    - marca
    - unidades
    - pickeadas
    - separadas
    - Pendiente Picking
    - Pendiente Separación
    - Efic. Picking
    - Efic. Separación
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                marca,
                COALESCE(SUM(uni), 0) as unidades,
                COALESCE(SUM(uni_pick), 0) as pickeadas,
                COALESCE(SUM(uni_sep), 0) as separadas,
                COALESCE(SUM(uni), 0) - COALESCE(SUM(uni_pick), 0) as pendiente_picking,
                COALESCE(SUM(uni), 0) - COALESCE(SUM(uni_sep), 0) as pendiente_separacion,
                CASE 
                    WHEN SUM(uni) > 0 THEN ROUND(SUM(uni_pick) * 100.0 / SUM(uni), 2)
                    ELSE 0 
                END as efic_picking,
                CASE 
                    WHEN SUM(uni) > 0 THEN ROUND(SUM(uni_sep) * 100.0 / SUM(uni), 2)
                    ELSE 0 
                END as efic_separacion
            FROM pedidos_grupo
            WHERE marca IS NOT NULL
            GROUP BY marca
            ORDER BY unidades DESC
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
    Retorna datos agrupados por canal con:
    - canal (cruce: grupos -> tiendas -> clientes)
    - unidades
    - pickeadas
    - separadas
    - Pendiente Picking
    - Pendiente Separación
    - Efic. Picking
    - Efic. Separación
    """
    try:
        init_database()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.canal,
                COALESCE(SUM(pg.uni), 0) as unidades,
                COALESCE(SUM(pg.uni_pick), 0) as pickeadas,
                COALESCE(SUM(pg.uni_sep), 0) as separadas,
                COALESCE(SUM(pg.uni), 0) - COALESCE(SUM(pg.uni_pick), 0) as pendiente_picking,
                COALESCE(SUM(pg.uni), 0) - COALESCE(SUM(pg.uni_sep), 0) as pendiente_separacion,
                CASE 
                    WHEN SUM(pg.uni) > 0 THEN ROUND(SUM(pg.uni_pick) * 100.0 / SUM(pg.uni), 2)
                    ELSE 0 
                END as efic_picking,
                CASE 
                    WHEN SUM(pg.uni) > 0 THEN ROUND(SUM(pg.uni_sep) * 100.0 / SUM(pg.uni), 2)
                    ELSE 0 
                END as efic_separacion
            FROM pedidos_grupo pg
            LEFT JOIN pedidos_tienda pt ON pg.id_tienda = pt.id_tienda
            LEFT JOIN clientes c ON pt.id_tienda = c.codigo
            WHERE c.canal IS NOT NULL
            GROUP BY c.canal
            ORDER BY unidades DESC
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
