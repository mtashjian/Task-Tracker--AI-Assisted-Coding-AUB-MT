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

This skeleton currently includes only the application entry point and a health check
endpoint. CRUD endpoints, business logic, and the JSON repository will be added in a
later step.

## Project Structure

```text
task-tracker/
├── app/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── repositories/
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

## Status

This is a bare skeleton. No CRUD endpoints, authentication, database, or frontend are
implemented yet. These will be added incrementally in later milestones.