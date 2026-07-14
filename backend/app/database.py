"""
Configuración y gestión de la base de datos SQLite para datos logísticos.
En Vercel el sistema de archivos es read-only; usamos /tmp para la BD.
"""
import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """
    Determina la ruta de la base de datos según el entorno.
    - En Vercel (VERCEL=1): usa /tmp (único directorio escribible)
    - En local: usa backend/app/data/
    """
    if os.environ.get("VERCEL"):
        # En Vercel el único directorio writable es /tmp
        return Path("/tmp") / "logistica.db"
    else:
        local_path = Path(__file__).resolve().parent / "data" / "logistica.db"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return local_path


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos, inicializando tablas si es necesario."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Crea las tablas si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT,
            canal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos_tienda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tienda TEXT,
            id_tienda TEXT,
            pedido_id TEXT,
            cantidad INTEGER,
            operador TEXT,
            turno TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos_grupo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            grupo TEXT,
            marca TEXT,
            id_tienda TEXT,
            pedido_id TEXT,
            uni INTEGER,
            uni_pick INTEGER,
            uni_sep INTEGER,
            horas_trabajadas REAL,
            categoria TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def clear_all_data():
    """Borra todos los datos de las tablas (para reimportación)."""
    init_database()
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
               (fecha, tienda, id_tienda, pedido_id, cantidad, operador, turno)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                row.get("fecha"),
                row.get("tienda"),
                row.get("id_tienda"),
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
               (fecha, grupo, marca, id_tienda, pedido_id, uni, uni_pick, uni_sep, horas_trabajadas, categoria)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row.get("fecha"),
                row.get("grupo"),
                row.get("marca"),
                row.get("id_tienda"),
                row.get("pedido_id"),
                row.get("uni"),
                row.get("uni_pick"),
                row.get("uni_sep"),
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
    init_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(uni) as total_unidades,
            SUM(horas_trabajadas) as total_horas
        FROM pedidos_grupo
        WHERE grupo NOT IN ('VIDRIERA', 'MATERIALES EMPAQUE', 'PACKAGING', 'PROMOCION')
    """)

    result = cursor.fetchone()
    conn.close()

    if result and result["total_horas"] and result["total_horas"] > 0:
        productividad = round(result["total_unidades"] / result["total_horas"], 0)
    else:
        productividad = 0

    return {
        "value": str(int(productividad)),
        "total_unidades": result["total_unidades"] if result else 0,
        "total_horas": result["total_horas"] if result else 0,
        "tiene_datos": bool(result and result["total_unidades"])
    }
