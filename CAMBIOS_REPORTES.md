# Cambios en Reportes de Status Preparación

## Resumen de Cambios

Se han actualizado los reportes del sistema para implementar la lógica correcta de datos según las especificaciones. Los cambios incluyen:

### 1. Exclusión de Grupos Específicos

**IMPORTANTE:** Todos los cálculos y reportes excluyen automáticamente los siguientes grupos:
- `VIDRIERA`
- `MATERIALES EMPAQUE`
- `PACKAGING`
- `PROMOCION`

Esta exclusión se aplica en:
- Resumen general
- Análisis por fecha
- Análisis por marca
- Análisis por canal
- Análisis por categoría
- Cálculo de productividad de picking

### 2. Actualización del Esquema de Base de Datos

#### Tabla `pedidos_tienda`
Se agregó el campo `id_tienda` para permitir el cruce con la tabla de clientes:
- `id_tienda`: Identificador de la tienda para relacionar con clientes

#### Tabla `pedidos_grupo`
Se actualizó completamente con los siguientes campos:
- `fecha`: Fecha del pedido
- `grupo`: Grupo de trabajo
- `marca`: Marca del producto
- `id_tienda`: Identificador de tienda (para cruce con clientes)
- `pedido_id`: ID del pedido
- `uni`: Total de unidades
- `uni_pick`: Unidades pickeadas
- `uni_sep`: Unidades separadas
- `horas_trabajadas`: Horas trabajadas
- `categoria`: Categoría del producto

### 2. Lógica de Reportes Actualizada

#### **Resumen General** (`/api/reportes/resumen`)
Muestra métricas agregadas del archivo grupos:
- Total Unidades (suma de `Uni`)
- Unidades Pickeadas (suma de `Uni.Pick`)
- Unidades Separadas (suma de `Uni.Sep`)
- Pendiente Picking (diferencia entre Total y Pickeadas)
- Pendiente Separación (diferencia entre Total y Separadas)
- Eficiencia Picking (% pickeadas/total)
- Eficiencia Separación (% separadas/total)
- Total de Registros

#### **Por Fecha** (`/api/reportes/por-fecha`)
Tabla detallada por fecha y marca:
- Fecha (orden descendente)
- Marca
- Unidades
- Pickeadas
- Separadas
- Efic. Picking (%)
- Efic. Separación (%)

#### **Por Marca** (`/api/reportes/por-marca`)
Tabla agregada por marca:
- Marca
- Unidades
- Pickeadas
- Separadas
- Pendiente Picking
- Pendiente Separación
- Efic. Picking (%)
- Efic. Separación (%)

#### **Por Canal** (`/api/reportes/por-canal`)
Tabla agregada por canal con cruces de datos:
- Canal (obtenido mediante: grupos → tiendas → clientes)
- Unidades
- Pickeadas
- Separadas
- Pendiente Picking
- Pendiente Separación
- Efic. Picking (%)
- Efic. Separación (%)

**Lógica de Cruce:**
```sql
pedidos_grupo → pedidos_tienda (por id_tienda) → clientes (por codigo)
```

### 3. Archivos Modificados

#### Backend
- [`backend/app/database.py`](file://backend/app/database.py): Esquema de base de datos actualizado
- [`backend/app/routers/reportes.py`](file://backend/app/routers/reportes.py): Endpoints con lógica de reportes
- [`backend/app/routers/upload.py`](file://backend/app/routers/upload.py): Parser de archivos actualizado

#### Frontend
- [`frontend/js/app.js`](file://frontend/js/app.js): 
  - Función `renderReport()` actualizada con nuevas columnas
  - Función `renderResumen()` con métricas correctas
  - Función `renderTable()` mejorada con labels personalizables

#### Archivos de Ejemplo
- [`ejemplos/generar_ejemplos.py`](file://ejemplos/generar_ejemplos.py): Generador actualizado
- [`ejemplos/pedidos_grupo.csv`](file://ejemplos/pedidos_grupo.csv): Con nuevos campos
- [`ejemplos/pedidos_tienda.csv`](file://ejemplos/pedidos_tienda.csv): Con id_tienda
- [`ejemplos/clientes.xlsx`](file://ejemplos/clientes.xlsx): Estructura original mantenida

### 4. Formato de Archivos de Entrada Esperados

#### `clientes.xlsx`
```
codigo | nombre | canal
C001   | ...    | B2B
```

#### `pedidos_tienda.csv` (separador `;`)
```
fecha;tienda;id_tienda;pedido_id;cantidad;operador;turno
```

#### `pedidos_grupo.csv` (separador `;`)
```
fecha;grupo;marca;id_tienda;pedido_id;Uni;Uni.Pick;Uni.Sep;horas_trabajadas;categoria
```

**Nota:** Los campos pueden tener variaciones de nombres (con mayúsculas, con puntos, etc.) y el parser los maneja automáticamente.

### 5. Uso del Sistema

1. **Importar Datos:**
   - Expandir la sección "Status Preparación" en el menú lateral
   - Hacer clic en "Importar Datos"
   - Seleccionar los 3 archivos requeridos
   - El sistema validará, procesará y cargará los datos

2. **Ver Reportes:**
   - Después de importar, seleccionar cualquier subcategoría:
     - **Resumen**: Vista general con métricas clave
     - **Por Fecha**: Análisis temporal por marca
     - **Por Marca**: Análisis agregado por marca
     - **Por Canal**: Análisis por canal de distribución
     - **Por Categoría**: Análisis por categoría de producto

### 6. Iniciar el Sistema

```bash
# Backend (terminal 1)
cd /workspace/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (terminal 2)
cd /workspace/frontend
python3 -m http.server 3000
```

Luego abrir en el navegador: `http://localhost:3000`

### 7. Notas Técnicas

- Los datos se almacenan en SQLite en `/tmp/logistica.db` (en producción Vercel) o `backend/app/data/logistica.db` (en desarrollo local)
- Los cruces de datos se realizan mediante JOINs en las consultas SQL
- Las eficiencias se calculan como porcentajes redondeados a 2 decimales
- Los archivos CSV deben usar separador `;` y encoding UTF-8
- **Todos los endpoints excluyen automáticamente los grupos:** `VIDRIERA`, `MATERIALES EMPAQUE`, `PACKAGING` y `PROMOCION`
- La exclusión se implementa mediante cláusula `WHERE grupo NOT IN (...)` en todas las consultas SQL

## Testing

Para probar el sistema con datos de ejemplo:

```bash
cd /workspace/ejemplos
python3 generar_ejemplos.py
```

Esto generará archivos de prueba que se pueden importar en el sistema.
