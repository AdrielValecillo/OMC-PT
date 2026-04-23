# OMC Leads API

API backend construida con FastAPI para gestionar leads comerciales y generar resúmenes ejecutivos con IA (Gemini) a partir de los datos captados.

## Tabla de contenido

- [1. Objetivo del proyecto](#1-objetivo-del-proyecto)
- [2. Stack tecnológico](#2-stack-tecnologico)
- [3. Arquitectura y estructura del repositorio](#3-arquitectura-y-estructura-del-repositorio)
- [4. Requisitos previos](#4-requisitos-previos)
- [5. Instalación y configuración](#5-instalacion-y-configuracion)
- [6. Variables de entorno](#6-variables-de-entorno)
- [7. Ejecución del proyecto](#7-ejecucion-del-proyecto)
- [8. Modelo de datos](#8-modelo-de-datos)
- [9. Endpoints de la API](#9-endpoints-de-la-api)
- [10. Integración con IA (Gemini)](#10-integracion-con-ia-gemini)
- [11. Seed de datos](#11-seed-de-datos)
- [12. Pruebas](#12-pruebas)
- [13. Flujo interno de la aplicación](#13-flujo-interno-de-la-aplicacion)
- [14. Solución de problemas comunes](#14-solucion-de-problemas-comunes)
- [15. Mejoras recomendadas](#15-mejoras-recomendadas)

## 1. Objetivo del proyecto

Este servicio permite:

- Crear, consultar, actualizar y eliminar leads (borrado lógico).
- Obtener métricas de negocio sobre leads.
- Generar un resumen ejecutivo automático con IA a partir de leads filtrados.
- Mantener una base técnica limpia y extensible para escenarios reales de captación comercial.

## 2. Stack tecnológico

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2 + pydantic-settings
- Uvicorn
- Psycopg (PostgreSQL)
- Google GenAI (`google-genai`)
- Pytest
- Ruff (dev dependency)
- `uv` como gestor de dependencias/entorno

## 3. Arquitectura y estructura del repositorio

```text
app/
  api/
    dependencies.py        # Inyección de dependencias (servicios, db, IA)
    routers/
      leads.py             # Endpoints HTTP de leads
  core/
    config.py              # Configuración central desde .env
  db/
    database.py            # Engine, SessionLocal, Base, create_tables()
    enums.py               # LeadSource
    models/
      lead.py              # Modelo ORM Lead
    repositories/
      lead_repository.py   # Acceso a datos
    schemas/
      lead.py              # DTOs request/response de FastAPI
  services/
    lead_service.py        # Lógica de negocio de leads
    ai_service.py          # Integración con Gemini
  main.py                  # App FastAPI, CORS y lifespan

scripts/
  seed_leads.py            # Carga inicial de leads de ejemplo (idempotente)

tests/
  conftest.py
  test_leads_api.py
  test_seed_script.py
```

### Capas principales

- **Router**: valida entrada/salida HTTP y mapea errores de negocio a `HTTPException`.
- **Service**: concentra reglas de negocio.
- **Repository**: encapsula consultas SQLAlchemy.
- **DB/Core**: sesiones, motor y configuración.

## 4. Requisitos previos

- Python 3.12
- `uv` instalado
- Base de datos PostgreSQL disponible (o SQLite para pruebas rápidas)
- API key de Gemini (opcional, pero necesaria para endpoint IA)

Instalar `uv` (si no lo tienes):

- Windows (PowerShell):
  - `pip install uv`

## 5. Instalación y configuración

1. Clonar repositorio:

```bash
git clone <url-del-repo>
cd OMC-PT
```

2. Sincronizar dependencias:

```bash
uv sync
```

3. Crear archivo `.env` en la raíz (ver sección de variables).

## 6. Variables de entorno

La app carga configuración con `pydantic-settings` desde `.env`.

Puedes definir la conexión de 2 formas:

### Opción A: URL completa

```env
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/omc_pt
```

### Opción B: Variables separadas

```env
DB_USER=usuario
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=omc_pt
```

### Variables adicionales

```env
APP_NAME=OMC Leads API
APP_VERSION=0.1.0
DB_AUTO_CREATE=true
API_KEY_GEMINI=tu_api_key_de_gemini
```

### CORS (opcional)

```env
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

> Nota: en desarrollo se permite `*`, en producción restringe orígenes explícitos.

## 7. Ejecución del proyecto

Levantar servidor en modo desarrollo:

```bash
uv run uvicorn app.main:app --reload
```

Con host/puerto explícitos:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

URLs útiles:

- API root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI JSON: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

## 8. Modelo de datos

Entidad principal: `Lead`

- `id` (int, PK)
- `nombre` (str, max 120)
- `email` (único, indexado)
- `telefono` (opcional)
- `fuente` (`LeadSource`)
- `producto_interes` (opcional)
- `presupuesto` (decimal)
- `created_at` / `updated_at`
- `deleted_at` (borrado lógico)

### Fuentes válidas (`LeadSource`)

- `instagram`
- `facebook`
- `landing_page`
- `referido`
- `otro`

## 9. Endpoints de la API

Base path: `/leads`

### 9.1 Crear lead

- **POST** `/leads`
- Status: `201`

Ejemplo body:

```json
{
  "nombre": "Juan Perez",
  "email": "juan.perez@example.com",
  "telefono": "+573001112244",
  "fuente": "instagram",
  "producto_interes": "Curso premium",
  "presupuesto": 350
}
```

Errores frecuentes:

- `409` si el email ya existe.
- `422` si falla validación de schema.

### 9.2 Listar leads

- **GET** `/leads`
- Query params:
  - `page` (default `1`)
  - `limit` (default `20`, máx `100`)
  - `fuente` (opcional)
  - `fecha_inicio` (opcional, datetime ISO)
  - `fecha_fin` (opcional, datetime ISO)

Validación:

- `400` si `fecha_inicio > fecha_fin`.

### 9.3 Obtener estadísticas

- **GET** `/leads/stats`
- Status: `200`
- Retorna:
  - `total_leads`
  - `leads_por_fuente`
  - `promedio_presupuesto`
  - `leads_ultimos_7_dias`

### 9.4 Resumen con IA

- **POST** `/leads/ai/summary`
- Status: `200` (si hay configuración de IA)
- Body opcional:

```json
{
  "fuente": "instagram",
  "fecha_inicio": "2026-04-23T18:10:50.877Z",
  "fecha_fin": "2026-04-23T18:10:50.877Z"
}
```

Comportamiento:

- Si encuentra leads con filtros -> genera resumen sobre ese subconjunto.
- Si no encuentra leads con filtros -> hace fallback automático a leads recientes y agrega nota en el resumen.
- Si no hay API key -> responde `503`.

### 9.5 Obtener lead por ID

- **GET** `/leads/{lead_id}`
- `404` si no existe o fue eliminado lógicamente.

### 9.6 Actualizar lead

- **PATCH** `/leads/{lead_id}`
- Actualización parcial.
- Errores:
  - `404` lead inexistente.
  - `409` email duplicado.

### 9.7 Eliminar lead (soft delete)

- **DELETE** `/leads/{lead_id}`
- Status: `204`
- El registro no se borra físicamente; se marca `deleted_at`.

## 10. Integración con IA (Gemini)

Servicio: `app/services/ai_service.py`

Detalles relevantes:

- Modelo configurado: `gemini-3-flash-preview`.
- Prompt de sistema orientado a análisis ejecutivo de marketing/ventas.
- Conversión de `Decimal` a `float` para serialización JSON.
- Si no hay datos de leads, retorna mensaje controlado.
- Si falta `API_KEY_GEMINI`, se lanza `AIConfigurationError` y API devuelve `503`.

## 11. Seed de datos

Script: `scripts/seed_leads.py`

Ejecutar:

```bash
uv run python scripts/seed_leads.py
```

Características:

- Crea tablas si no existen.
- Inserta leads de ejemplo.
- Es idempotente por email (no duplica en ejecuciones repetidas).

## 12. Pruebas

Ejecutar suite:

```bash
uv run pytest -q
```

Incluye pruebas de:

- CRUD básico de leads.
- Paginación y filtros.
- Stats.
- Resumen IA (casos exitosos y falta de API key).
- Idempotencia de seed.

## 13. Flujo interno de la aplicación

1. `app/main.py` crea app FastAPI y CORS.
2. `lifespan` ejecuta `create_tables()` si `DB_AUTO_CREATE=true`.
3. Dependencia `get_db` entrega una sesión SQLAlchemy por request.
4. Router delega a servicios (`LeadService`, `AIService`).
5. Servicios usan repositorios para persistencia y consultas.
6. Schemas de Pydantic garantizan contratos de entrada/salida.

## 14. Solución de problemas comunes

### 14.1 Error `ModuleNotFoundError: pydantic._internal._signature`

Causa probable: ejecutar con Python global incompatible (por ejemplo, `pydantic` viejo).

Solución:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Evita arrancar con `uvicorn` global fuera del entorno de `uv`.

### 14.2 Swagger muestra `Failed to fetch`

Posibles causas:

- El servidor no está corriendo.
- El proceso Uvicorn se detuvo.
- URL de docs no corresponde al host/puerto actual.

Checklist:

1. Confirma que corre `http://127.0.0.1:8000/`.
2. Reabre `http://127.0.0.1:8000/docs`.
3. Haz hard refresh (`Ctrl+F5`).

### 14.3 `/leads/ai/summary` responde sin datos útiles

Si el filtro no encuentra registros, el endpoint ahora aplica fallback a leads recientes para no devolver vacío.

### 14.4 Error `503` en IA

Configura:

```env
API_KEY_GEMINI=<tu_api_key>
```

Y reinicia servidor.

## 15. Mejoras recomendadas

- Migraciones con Alembic en lugar de `create_all`.
- Autenticación y autorización para endpoints sensibles.
- Observabilidad (logs estructurados, tracing, métricas).
- Limitación de tasa y control de costos para llamadas de IA.
- Tests de integración con base PostgreSQL real (pipeline CI).
- Endpoints async y capa de configuración por ambientes (dev/staging/prod).

---

Si quieres, en un siguiente paso te agrego también:

- diagrama de arquitectura en `README`,
- colección de requests lista para Postman/Insomnia,
- y sección de despliegue (Docker + variables para producción).
