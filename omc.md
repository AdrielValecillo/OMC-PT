# OMC PT - Backend Leads API (FastAPI)

API REST para gestionar leads, con enfoque en buenas practicas, arquitectura por capas y base preparada para integrar IA (fase siguiente).

## Stack tecnico

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL (recomendado: Supabase) o SQLite para pruebas locales
- `uv` como package manager
- Pytest + TestClient para pruebas
- Ruff para lint

## Estructura del proyecto

Se usa la estructura existente del repositorio:

- `app/main.py`: bootstrap de FastAPI, CORS, startup y registro de routers.
- `app/core/config.py`: configuracion central por variables de entorno.
- `app/db/database.py`: engine, sesion y `create_tables()`.
- `app/db/models/`: modelos ORM.
- `app/db/schemas/`: contratos Pydantic de entrada/salida.
- `app/db/repositories/`: acceso a datos.
- `app/services/`: logica de negocio.
- `app/api/routers/`: endpoints HTTP.
- `scripts/seed_leads.py`: seed manual, aislado e idempotente.
- `tests/`: pruebas automatizadas.

## Variables de entorno

Copia `.env.example` a `.env` y ajusta valores.

Variables clave:

- `DATABASE_URL` (recomendada para Supabase)
- o `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- `DB_AUTO_CREATE=true` para crear tablas en startup

## Instalacion

```bash
uv sync
```

## Ejecutar API

```bash
uv run uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`.

Swagger: `http://127.0.0.1:8000/docs`

## Comportamiento de schema

Al levantar el servidor, si `DB_AUTO_CREATE=true`, se ejecuta:

- `Base.metadata.create_all(...)`

Esto crea tablas faltantes automaticamente. No reemplaza migraciones complejas; para esta prueba tecnica acelera el desarrollo.

## Ejecutar seed (manual, una sola vez cuando lo requieras)

El seed NO corre en startup.

```bash
uv run python scripts/seed_leads.py
```

Caracteristicas:

- script aislado
- idempotente por email (si ya existe, no reinserta)
- inserta 10 leads de ejemplo

## Endpoints implementados

- `POST /leads`
- `GET /leads`
- `GET /leads/{id}`
- `PATCH /leads/{id}`
- `DELETE /leads/{id}` (soft delete)
- `GET /leads/stats`

### Validaciones

- `nombre` minimo 2 caracteres
- `email` valido y unico
- `fuente` en: `instagram`, `facebook`, `landing_page`, `referido`, `otro`
- errores HTTP claros:
  - `409` para email duplicado
  - `404` para recurso inexistente
  - `400` para rango de fechas invalido en listado

## Ejemplos rapidos con curl

Crear lead:

```bash
curl -X POST "http://127.0.0.1:8000/leads" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Perez",
    "email": "juan.perez@example.com",
    "fuente": "instagram",
    "presupuesto": 350
  }'
```

Listar con filtros:

```bash
curl "http://127.0.0.1:8000/leads?page=1&limit=10&fuente=instagram"
```

Estadisticas:

```bash
curl "http://127.0.0.1:8000/leads/stats"
```

## Pruebas

Ejecutar toda la suite:

```bash
uv run pytest
```

Modo verbose:

```bash
uv run pytest -v
```

Un solo archivo:

```bash
uv run pytest tests/test_leads_api.py
```

Un test puntual (funcion):

```bash
uv run pytest tests/test_leads_api.py::test_create_lead
```

Seed idempotente:

```bash
uv run pytest tests/test_seed_script.py::test_seed_is_idempotent
```

## Lint y checks

Lint:

```bash
uv run ruff check app tests scripts
```

Chequeo sintactico:

```bash
uv run python -m compileall app tests scripts
```

## Estado de IA (siguiente fase)

La base de arquitectura ya esta lista para agregar:

- `POST /leads/ai/summary`
- proveedor Google (Gemini)
- servicio desacoplado para no mezclar logica HTTP con integracion LLM

## Notas de entrega

- No se suben secretos (`.env` esta gitignore).
- Se incluye `.env.example`.
- El seed es manual y aislado como pediste.
