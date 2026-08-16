# Task Tracker API

A minimal, learning-focused REST API for tracking tasks, built with **FastAPI** and **Pydantic**.

This project is designed to teach core backend concepts — REST endpoint design, request
validation, business rule enforcement, error handling, persistence, and API testing —
without the added complexity of a database.

## Architecture

Per [ADR-001](#), this project uses local **JSON file storage** instead of a database.
The application is layered as follows:

- **Routes** — handle HTTP concerns only
- **Pydantic models** — validate request and response data
- **Services** — enforce business rules
- **Repositories** — read from and write to the JSON data file

## Project Structure

```text
task-tracker/
├── app/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── repositories/
├── frontend/
│   └── index.html
├── data/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- pip

## Setup

1. Create and activate a virtual environment:

```powershell
   python -m venv venv
   venv\Scripts\activate
```

2. Install dependencies:

```powershell
   pip install -r requirements.txt
```

3. Copy the example environment file and adjust if needed:

```powershell
   copy .env.example .env
```

## Running the Server

Start the development server with auto-reload:

```powershell
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## Testing the Health Endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "timestamp": "2026-07-27T12:34:56.789012+00:00"
}
```

## API Documentation (Swagger UI)

Once the server is running, open your browser to:

```text
http://127.0.0.1:8000/docs
```

This provides an interactive Swagger UI for exploring and testing the API.

## Opening the Frontend

The board is a static page at `frontend/index.html`. There is no build step.

1. Start the API first (see [Running the Server](#running-the-server)). The page calls `http://localhost:8000`.
2. Open `frontend/index.html` with the Live Server extension. The board is at:

```text
http://127.0.0.1:5500/index.html
```

CORS already allows `http://127.0.0.1:5500` and `http://localhost:5500`.

## Running Tests

From the `task-tracker/` directory, with the virtual environment activated:

```powershell
pytest tests/test_tasks.py
```

## Status

Task CRUD, due-date/overdue and search filters, and a static Kanban frontend are
implemented. There is no database or authentication.