"""
Script para generar archivos de ejemplo para testing
"""
import csv
import random
from datetime import datetime, timedelta
import openpyxl

# ==================== GENERAR CLIENTES.XLSX ====================
print("Generando clientes.xlsx...")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Clientes"

# Encabezados
ws.append(["codigo", "nombre", "canal"])

# Datos de ejemplo
clientes_data = [
    ["C001", "Tienda Centro", "B2B"],
    ["C002", "Tienda Norte", "B2B"],
    ["C003", "Tienda Sur", "B2B"],
    ["C004", "Marketplace Principal", "E-commerce"],
    ["C005", "Tienda Oeste", "B2B"],
    ["C006", "Outlet Factory", "B2B"],
    ["C007", "E-commerce Propio", "E-commerce"],
    ["C008", "Distribuidor Mayorista", "B2B"],
]

for row in clientes_data:
    ws.append(row)

wb.save("clientes.xlsx")
print("✓ clientes.xlsx creado")

# ==================== GENERAR PEDIDOS_TIENDA.CSV ====================
print("Generando pedidos_tienda.csv...")

with open("pedidos_tienda.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Encabezados con id_tienda
    writer.writerow(["fecha", "tienda", "id_tienda", "pedido_id", "cantidad", "operador", "turno"])
    
    # Generar 50 registros de ejemplo
    operadores = ["Juan P.", "María L.", "Carlos R.", "Ana G.", "Pedro M.", "Lucía S."]
    tiendas_info = [
        ("Centro", "C001"),
        ("Norte", "C002"),
        ("Sur", "C003"),
        ("Oeste", "C005"),
        ("Outlet", "C006"),
        ("Online", "C007")
    ]
    turnos = ["Mañana", "Tarde"]
    
    fecha_base = datetime(2026, 7, 1)
    
    for i in range(50):
        fecha = (fecha_base + timedelta(days=random.randint(0, 13))).strftime("%Y-%m-%d")
        tienda, id_tienda = random.choice(tiendas_info)
        pedido_id = f"PED{1000 + i}"
        cantidad = random.randint(20, 150)
        operador = random.choice(operadores)
        turno = random.choice(turnos)
        
        writer.writerow([fecha, tienda, id_tienda, pedido_id, cantidad, operador, turno])

print("✓ pedidos_tienda.csv creado")

# ==================== GENERAR PEDIDOS_GRUPO.CSV ====================
print("Generando pedidos_grupo.csv...")

with open("pedidos_grupo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Encabezados con nuevos campos: marca, id_tienda, Uni, Uni.Pick, Uni.Sep
    writer.writerow(["fecha", "grupo", "marca", "id_tienda", "pedido_id", "Uni", "Uni.Pick", "Uni.Sep", "horas_trabajadas", "categoria"])
    
    # Generar 60 registros de ejemplo
    grupos = ["Grupo A", "Grupo B", "Grupo C", "Grupo D", "VIDRIERA", "MATERIALES EMPAQUE", "PACKAGING", "PROMOCION"]
    marcas = ["Nike", "Adidas", "Puma", "Reebok", "New Balance"]
    categorias = ["Apparel", "Calzado", "Accesorios"]
    tiendas_ids = ["C001", "C002", "C003", "C005", "C006", "C007"]
    
    for i in range(60):
        fecha = (fecha_base + timedelta(days=random.randint(0, 13))).strftime("%Y-%m-%d")
        grupo = random.choice(grupos)
        marca = random.choice(marcas)
        id_tienda = random.choice(tiendas_ids)
        pedido_id = f"PED{2000 + i}"
        uni = random.randint(100, 500)
        # Uni.Pick será entre 70-100% de Uni
        uni_pick = int(uni * random.uniform(0.70, 1.0))
        # Uni.Sep será entre 60-95% de Uni
        uni_sep = int(uni * random.uniform(0.60, 0.95))
        horas_trabajadas = round(random.uniform(1.5, 6.0), 2)
        categoria = random.choice(categorias)
        
        writer.writerow([fecha, grupo, marca, id_tienda, pedido_id, uni, uni_pick, uni_sep, horas_trabajadas, categoria])

print("✓ pedidos_grupo.csv creado")

print("\n✅ Todos los archivos de ejemplo han sido creados exitosamente!")
print("\nArchivos generados:")
print("  - clientes.xlsx")
print("  - pedidos_tienda.csv")
print("  - pedidos_grupo.csv")
