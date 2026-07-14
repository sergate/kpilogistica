# Nueva Funcionalidad: KPI de Productividad con Importación de Datos

## 📋 Resumen

Se ha implementado una nueva funcionalidad en el KPI **"Productividad picking (B-03)"** que permite importar datos desde archivos externos (Excel y CSV) y almacenarlos en una base de datos SQLite para su consulta posterior.

## 🎯 Características Implementadas

### 1. **Base de Datos SQLite**
- Base de datos local: `/workspace/backend/app/data/logistica.db`
- Tres tablas:
  - `clientes` - Datos de clientes desde Excel
  - `pedidos_tienda` - Pedidos por tienda desde CSV
  - `pedidos_grupo` - Pedidos por grupo desde CSV (usado para calcular productividad)

### 2. **Interfaz de Importación**
Al hacer clic en el KPI **"Productividad picking (B-03)"**, se abre un modal con:
- **3 campos de carga de archivos:**
  1. Archivo de Clientes (Excel `.xlsx`)
  2. Pedidos por Tienda (CSV con separador `;` y comillas)
  3. Pedidos por Grupo (CSV con separador `;` y comillas)
- **Botón "Procesar Datos":** Carga los archivos a la base de datos
- **Botón "Borrar Datos Actuales":** Elimina todos los datos importados anteriormente

### 3. **Endpoints API Nuevos**

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/upload-files` | Recibe los 3 archivos y los procesa |
| GET | `/api/picking-data` | Retorna datos de productividad desde la BD |
| DELETE | `/api/clear-data` | Borra todos los datos de las tablas |

### 4. **Cálculo Automático**
La productividad se calcula automáticamente como:
```
Productividad = Total Unidades / Total Horas Trabajadas
```
Usando los datos de la tabla `pedidos_grupo`.

## 📁 Archivos Modificados

```
✨ NUEVOS:
├── backend/app/database.py       # Gestión de base de datos SQLite
├── backend/app/routers/upload.py # Endpoints de carga de archivos
└── ejemplos/                     # Archivos de ejemplo para testing
    ├── clientes.xlsx
    ├── pedidos_tienda.csv
    ├── pedidos_grupo.csv
    └── generar_ejemplos.py       # Script para regenerar ejemplos

✏️ MODIFICADOS:
├── backend/app/main.py           # Incluye nuevo router de upload
├── requirements.txt              # +openpyxl, +python-multipart
├── backend/requirements.txt      # Actualizado
├── frontend/index.html           # Modal de importación
├── frontend/js/app.js            # Lógica de importación
└── frontend/css/styles.css       # Estilos del modal
```

## 🚀 Cómo Usar

### 1. **Prueba Local**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
cd backend
uvicorn app.main:app --reload --port 8000

# Abrir en navegador
http://localhost:8000
```

### 2. **Probar la Importación**
1. Hacer clic en el KPI **"B-03 Productividad picking"**
2. Se abrirá el modal de importación
3. Seleccionar los 3 archivos de ejemplo desde `/workspace/ejemplos/`
4. Hacer clic en **"Procesar Datos"**
5. Esperar confirmación (verás cuántos registros se importaron)
6. La productividad se calculará automáticamente

### 3. **Reimportar Datos**
Si quieres cargar nuevos archivos:
1. Abrir el modal de importación
2. Hacer clic en **"Borrar Datos Actuales"**
3. Confirmar la acción
4. Seleccionar los nuevos archivos
5. Hacer clic en **"Procesar Datos"**

## 📝 Formato de Archivos

### **clientes.xlsx**
```
| codigo | nombre              | canal       |
|--------|---------------------|-------------|
| C001   | Tienda Centro       | B2B         |
| C002   | Tienda Norte        | B2B         |
| C004   | E-commerce Propio   | E-commerce  |
```

### **pedidos_tienda.csv**
```csv
fecha;tienda;pedido_id;cantidad;operador;turno
2026-07-01;Centro;PED1001;120;Juan P.;Mañana
2026-07-02;Norte;PED1002;85;María L.;Tarde
```

### **pedidos_grupo.csv** (usado para productividad)
```csv
fecha;grupo;pedido_id;unidades;horas_trabajadas;categoria
2026-07-01;Grupo A;PED2001;450;3.5;Apparel
2026-07-02;Grupo B;PED2002;320;2.8;Calzado
```

## 🔧 Archivos de Ejemplo

Los archivos de ejemplo están en [`/workspace/ejemplos/`](file://ejemplos/).

Para regenerar los archivos de ejemplo:
```bash
cd ejemplos
python3 generar_ejemplos.py
```

## 📊 Base de Datos

### Estructura de Tablas

**clientes**
- `id` (INTEGER, PRIMARY KEY)
- `codigo` (TEXT)
- `nombre` (TEXT)
- `canal` (TEXT)
- `created_at` (TIMESTAMP)

**pedidos_tienda**
- `id` (INTEGER, PRIMARY KEY)
- `fecha` (TEXT)
- `tienda` (TEXT)
- `pedido_id` (TEXT)
- `cantidad` (INTEGER)
- `operador` (TEXT)
- `turno` (TEXT)
- `created_at` (TIMESTAMP)

**pedidos_grupo** (base del cálculo)
- `id` (INTEGER, PRIMARY KEY)
- `fecha` (TEXT)
- `grupo` (TEXT)
- `pedido_id` (TEXT)
- `unidades` (INTEGER) ⭐
- `horas_trabajadas` (REAL) ⭐
- `categoria` (TEXT)
- `created_at` (TIMESTAMP)

## 🚢 Deploy en Vercel

Ya está todo configurado para desplegarse en Vercel. Solo necesitas hacer:

```bash
git add .
git commit -m "Agregar funcionalidad de importación de datos"
git push origin main
```

Vercel detectará los cambios automáticamente y desplegará la nueva versión.

⚠️ **Nota:** SQLite funciona en Vercel, pero los datos se pierden entre deployments. Para producción, considera migrar a:
- **PostgreSQL** (Supabase, Railway, Neon)
- **MySQL** (PlanetScale)
- **Vercel Postgres**

## 🔍 Validaciones Implementadas

- ✅ Validación de extensiones de archivo (.xlsx, .csv)
- ✅ Validación de archivos obligatorios (los 3 deben estar presentes)
- ✅ Manejo de errores en parsing de archivos
- ✅ Separador CSV correcto (`;` y comillas)
- ✅ Cálculo seguro de productividad (evita división por cero)

## 🎨 Interfaz

El modal de importación incluye:
- 🎨 Diseño consistente con el resto del dashboard
- 📱 Responsive (funciona en móviles)
- ⚡ Mensajes de estado en tiempo real
- ✨ Animaciones suaves
- 🔒 Confirmación antes de borrar datos

## 🤝 Próximos Pasos Sugeridos

1. **Conectar fuente de datos real** (en lugar de archivos manuales)
2. **Agregar historial de importaciones** (fecha, usuario, cantidad de registros)
3. **Visualización de datos importados** (tabla con paginación)
4. **Exportar datos a Excel** desde el KPI
5. **Programar importaciones automáticas** (cron job)
6. **Migrar a base de datos persistente** para producción

---

✅ **Todo está listo para probar y desplegar!**

Para cualquier duda sobre la implementación, revisa los archivos:
- [`backend/app/database.py`](file://backend/app/database.py) - Lógica de base de datos
- [`backend/app/routers/upload.py`](file://backend/app/routers/upload.py) - Endpoints de carga
- [`frontend/js/app.js`](file://frontend/js/app.js) - Lógica del frontend
