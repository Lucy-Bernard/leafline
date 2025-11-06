# Plant Care API

## Install uv

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install Dependencies

```
uv sync
```

## Set .env

1. Create `.env` file.

```
touch .env
```

2. In `.env`, set the following variables:

```
ENVIRONMENT=local
OPENROUTER_API_KEY=your_openrouter_api_key_here
PLANT_ID_API_KEY=your_plant_id_api_key_here
DATABASE_URL=your_database_url_here
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here
```

### Environment Configuration

The `ENVIRONMENT` variable controls CORS origins:
- `local`: Allows `http://localhost:3000`
- `dev`: Allows `https://dev.yourapp.com` (update in `config/cors.py`)
- `prod`: Allows `https://yourapp.com` (update in `config/cors.py`)

## Run Project

```
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or using FastAPI CLI:

```
uv run fastapi dev main.py
```

## Code Quality

Ruff is configured as a project tool (no separate installation needed with `uv sync`).

### Lint

```
uv run ruff check .
```

### Format

```
uv run ruff format .
```

### Type Check

```
uv run ruff check .
```

## API Usage

### Direct Care Schedule Generation

- **Endpoint:** POST /api/v1/generate-care-schedule

- **Request Body:**
  ```json
  {
    "plant_name": "Monstera Deliciosa"
  }
  ```

- **Response:**
  ```json
  {
    "plant_name": "Monstera Deliciosa",
    "care_instructions": "Provide bright, indirect sunlight...",
    "watering_schedule": "Water thoroughly every 1-2 weeks..."
  }
  ```

### Plant Creation via Image Identification (CRUD Create)

- **Endpoint:** POST /api/v1/plants

- **Request Body:** (Base64-encoded image; latitude/longitude optional)
  ```json
  {
    "image": "data:image/jpg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/... (full base64)",
    "latitude": 49.207,
    "longitude": 16.608
  }
  ```

- **Response:** (Identified plant with generated care schedule)
  ```json
  {
    "id": "uuid-here",
    "name": "Leucojum vernum",
    "care_schedule": {
      "plant_name": "Leucojum vernum",
      "care_instructions": "...",
      "watering_schedule": "..."
    }
  }
  ```

- **Notes:** Requires valid Plant.id API key. Identification uses top suggestion if probability >= 0.5. Image must be base64 (data:image/... format).

Visit http://localhost:8000/docs for interactive API documentation.