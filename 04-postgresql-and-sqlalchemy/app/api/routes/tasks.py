from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.tasks import TaskCreate, TaskPage, TaskResponse, TaskUpdate
from app.services.tasks import TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DbSession) -> TaskResponse:
    return TaskService(db).create(payload)


@router.get("", response_model=TaskPage)
def list_tasks(
    db: DbSession,
    completed: bool | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> TaskPage:
    return TaskService(db).list(completed, limit, offset)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: DbSession,
) -> TaskResponse:
    try:
        return TaskService(db).update(task_id, payload)
    except TaskNotFoundError as exc:
        raise HTTPException(404, "Task not found") from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbSession) -> Response:
    try:
        TaskService(db).delete(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(404, "Task not found") from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
