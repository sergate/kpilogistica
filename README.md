# KPI Logística

Panel de KPIs operativos del depósito: sidebar con los indicadores agrupados
por zona (Recepción, Picking, Put-to-Wall/Packing, Despacho) y un panel
central con el detalle de cada KPI seleccionado.

## Estructura

```
kpilogistica/
├── backend/               # API (FastAPI / Python)
│   ├── app/
│   │   ├── main.py        # punto de entrada de la app
│   │   ├── routers/
│   │   │   └── kpis.py    # endpoints /api/zones, /api/kpis, /api/kpis/{id}
│   │   └── data/
│   │       └── kpis.json  # datos de ejemplo (reemplazar por WMS/DB real)
│   └── requirements.txt
├── frontend/               # UI estática (HTML/CSS/JS, sin build step)
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
└── README.md
```

## Cómo correrlo localmente

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000
```

Abrir `http://localhost:8000` — el backend sirve el frontend estático y expone
la API en `/api/*`.

## Deploy en Vercel

El repo ya está preparado para desplegarse tal cual en Vercel (frontend +
backend en un solo deploy, sin servidores propios):

1. Entrar a [vercel.com](https://vercel.com) → **Add New → Project** →
   importar el repo `sergate/kpilogistica` desde GitHub.
2. Framework Preset: dejarlo en **Other** (Vercel detecta FastAPI solo por
   `pyproject.toml` / `requirements.txt`).
3. Root Directory: dejar **vacío** (no poner `./`).
4. Build Command / Output Directory: dejar vacíos — no aplica, es una función
   Python.
5. Deploy.

Cómo funciona la configuración:
- `pyproject.toml` le indica a Vercel que el entrypoint de la app es
  `backend/app/main.py` (ahí vive la instancia `app` de FastAPI).
- Esa función sirve tanto la API (`/api/*`) como el frontend estático
  (`frontend/`), igual que en local.
- `requirements.txt` en la raíz es lo que Vercel usa para detectar que es un
  proyecto Python e instalar las dependencias.
- `.python-version` fija la versión de Python (3.12).

Una vez desplegado, Vercel te da una URL tipo
`https://kpilogistica.vercel.app` con todo funcionando — frontend en `/` y
API en `/api/zones`, `/api/kpis`, `/api/kpis/{id}`.

## Endpoints

| Método | Ruta                | Descripción                              |
|--------|---------------------|-------------------------------------------|
| GET    | `/api/zones`        | Zonas operativas y KPIs de cada una       |
| GET    | `/api/kpis`         | Detalle de todos los KPIs                 |
| GET    | `/api/kpis/{id}`    | Detalle de un KPI puntual                 |

## Conectar datos reales

Reemplazar la función `load_data()` en `backend/app/routers/kpis.py` por una
consulta real (WMS, base de datos, export periódico, etc.), manteniendo la
misma forma de respuesta que hoy devuelve `kpis.json`.

## Próximos pasos sugeridos

- Autenticación básica si el panel se expone fuera de la red interna.
- Filtro por rango de fechas y comparación entre marcas (Cheeky / Como Quieres).
- Exportar el KPI visible a Excel.
- Job programado que actualice `kpis.json` (o una base de datos) desde el WMS.
