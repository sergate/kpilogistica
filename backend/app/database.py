"""
Configuración y gestión de la base de datos SQLite para datos logísticos.
"""
import sqlite3
from pathlib import Path
from typing import Optional

# Base de datos en el directorio backend/app/data
DB_PATH = Path(__file__).resolve().parent / "data" / "logistica.db"

# Asegurar que el directorio exista
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Crea las tablas si no existen."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tabla de Clientes (desde el Excel)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL,
                nombre TEXT,
                canal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Pedidos por Tienda (CSV 1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_tienda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tienda TEXT,
                pedido_id TEXT,
                cantidad INTEGER,
                operador TEXT,
                turno TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Pedidos por Grupo (CSV 2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_grupo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                grupo TEXT,
                pedido_id TEXT,
                unidades INTEGER,
                horas_trabajadas REAL,
                categoria TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")


def clear_all_data():
    """Borra todos los datos de las tablas (para reimportación)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM pedidos_tienda")
    cursor.execute("DELETE FROM pedidos_grupo")
    
    conn.commit()
    conn.close()


def insert_clientes(data: list[dict]):
    """Inserta registros de clientes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    for row in data:
        cursor.execute(
            "INSERT INTO clientes (codigo, nombre, canal) VALUES (?, ?, ?)",
            (row.get("codigo"), row.get("nombre"), row.get("canal"))
        )
    
    conn.commit()
    conn.close()


def insert_pedidos_tienda(data: list[dict]):
    """Inserta registros de pedidos por tienda."""
    conn = get_connection()
    cursor = conn.cursor()
    
    for row in data:
        cursor.execute(
            """INSERT INTO pedidos_tienda 
               (fecha, tienda, pedido_id, cantidad, operador, turno) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                row.get("fecha"),
                row.get("tienda"),
                row.get("pedido_id"),
                row.get("cantidad"),
                row.get("operador"),
                row.get("turno")
            )
        )
    
    conn.commit()
    conn.close()


def insert_pedidos_grupo(data: list[dict]):
    """Inserta registros de pedidos por grupo."""
    conn = get_connection()
    cursor = conn.cursor()
    
    for row in data:
        cursor.execute(
            """INSERT INTO pedidos_grupo 
               (fecha, grupo, pedido_id, unidades, horas_trabajadas, categoria) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                row.get("fecha"),
                row.get("grupo"),
                row.get("pedido_id"),
                row.get("unidades"),
                row.get("horas_trabajadas"),
                row.get("categoria")
            )
        )
    
    conn.commit()
    conn.close()


def get_productividad_picking() -> dict:
    """
    Calcula la productividad de picking desde la base de datos.
    Retorna un diccionario con el valor calculado y detalles.
    """
    # Asegurar que la BD esté inicializada
    try:
        init_database()
    except:
        pass
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Consulta para calcular productividad (unidades / hora / operador)
    cursor.execute("""
        SELECT 
            SUM(unidades) as total_unidades,
            SUM(horas_trabajadas) as total_horas
        FROM pedidos_grupo
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result["total_horas"] and result["total_horas"] > 0:
        productividad = round(result["total_unidades"] / result["total_horas"], 0)
    else:
        productividad = 0
    
    return {
        "value": str(productividad),
        "total_unidades": result["total_unidades"] if result else 0,
        "total_horas": result["total_horas"] if result else 0
    }

