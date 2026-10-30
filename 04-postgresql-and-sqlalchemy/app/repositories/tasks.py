from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list(
        self,
        *,
        completed: bool | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Task], int]:
        filters = [] if completed is None else [Task.completed.is_(completed)]

        query = (
            select(Task)
            .where(*filters)
            .order_by(Task.id)
            .limit(limit)
            .offset(offset)
        )
        items = list(self.db.scalars(query))

        count_query = select(func.count()).select_from(Task).where(*filters)
        total = self.db.scalar(count_query) or 0

        return items, total

    def add(self, title: str) -> Task:
        task = Task(title=title)
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
