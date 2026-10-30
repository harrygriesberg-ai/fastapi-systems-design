from sqlalchemy.orm import Session

from app.repositories.tasks import TaskRepository
from app.schemas.tasks import TaskCreate, TaskPage, TaskResponse, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TaskRepository(db)

    def create(self, payload: TaskCreate) -> TaskResponse:
        try:
            task = self.repo.add(payload.title)
            self.db.commit()
            self.db.refresh(task)
            return TaskResponse.model_validate(task)
        except Exception:
            self.db.rollback()
            raise

    def list(
        self,
        completed: bool | None,
        limit: int,
        offset: int,
    ) -> TaskPage:
        items, total = self.repo.list(
            completed=completed,
            limit=limit,
            offset=offset,
        )
        return TaskPage(
            items=[TaskResponse.model_validate(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    def update(self, task_id: int, payload: TaskUpdate) -> TaskResponse:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        try:
            self.db.commit()
            self.db.refresh(task)
            return TaskResponse.model_validate(task)
        except Exception:
            self.db.rollback()
            raise

    def delete(self, task_id: int) -> None:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        try:
            self.repo.delete(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
