from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task Tracker API",
    description="A learning-focused Task Tracker REST API built with FastAPI.",
    version="0.1.0",
)

# Add CORS middleware immediately after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """
    Simple liveness check endpoint.

    Returns:
        dict: A status payload indicating the API is running, along with
        the current UTC timestamp in ISO 8601 format.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    search: str | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(
        status=status, priority=priority, overdue=overdue, search=search
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    existing = storage.get_task_by_id(task_id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    other_fields = payload.model_fields_set - {"status"}
    if payload.status is not None and (payload.status != existing.status or not other_fields):
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )