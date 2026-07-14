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
    
    # Encabezados
    writer.writerow(["fecha", "tienda", "pedido_id", "cantidad", "operador", "turno"])
    
    # Generar 50 registros de ejemplo
    operadores = ["Juan P.", "María L.", "Carlos R.", "Ana G.", "Pedro M.", "Lucía S."]
    tiendas = ["Centro", "Norte", "Sur", "Oeste", "Outlet", "Online"]
    turnos = ["Mañana", "Tarde"]
    
    fecha_base = datetime(2026, 7, 1)
    
    for i in range(50):
        fecha = (fecha_base + timedelta(days=random.randint(0, 13))).strftime("%Y-%m-%d")
        tienda = random.choice(tiendas)
        pedido_id = f"PED{1000 + i}"
        cantidad = random.randint(20, 150)
        operador = random.choice(operadores)
        turno = random.choice(turnos)
        
        writer.writerow([fecha, tienda, pedido_id, cantidad, operador, turno])

print("✓ pedidos_tienda.csv creado")

# ==================== GENERAR PEDIDOS_GRUPO.CSV ====================
print("Generando pedidos_grupo.csv...")

with open("pedidos_grupo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Encabezados
    writer.writerow(["fecha", "grupo", "pedido_id", "unidades", "horas_trabajadas", "categoria"])
    
    # Generar 60 registros de ejemplo
    grupos = ["Grupo A", "Grupo B", "Grupo C", "Grupo D"]
    categorias = ["Apparel", "Calzado", "Accesorios"]
    
    for i in range(60):
        fecha = (fecha_base + timedelta(days=random.randint(0, 13))).strftime("%Y-%m-%d")
        grupo = random.choice(grupos)
        pedido_id = f"PED{2000 + i}"
        unidades = random.randint(100, 500)
        horas_trabajadas = round(random.uniform(1.5, 6.0), 2)
        categoria = random.choice(categorias)
        
        writer.writerow([fecha, grupo, pedido_id, unidades, horas_trabajadas, categoria])

print("✓ pedidos_grupo.csv creado")

print("\n✅ Todos los archivos de ejemplo han sido creados exitosamente!")
print("\nArchivos generados:")
print("  - clientes.xlsx")
print("  - pedidos_tienda.csv")
print("  - pedidos_grupo.csv")
