from datetime import date, datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    search: Optional[str] = None,
) -> list[TaskResponse]:
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if overdue is not None:
        today = date.today()
        tasks = [
            task
            for task in tasks
            if (
                task.due_date is not None
                and task.due_date < today
                and task.status != TaskStatus.DONE
            ) == overdue
        ]
    if search is not None and search.strip():
        needle = search.strip().casefold()
        tasks = [
            task
            for task in tasks
            if needle in task.title.casefold()
            or needle in task.description.casefold()
            or (task.assignee is not None and needle in task.assignee.casefold())
        ]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return existing

    updated = existing.model_copy(
        update={**updates, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
