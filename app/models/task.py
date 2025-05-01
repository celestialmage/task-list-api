import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from ..db import db

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=True, default=None)

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }

        if self.completed_at:
            task_dict["completed_at"] = self.completed_at
        else:
            task_dict["is_complete"] = False

        return task_dict
    
    @classmethod
    def from_dict(cls, task_data):
        new_task = Task(title=task_data["title"], 
                        description=task_data["description"], 
                        completed_at=task_data["completed_at"] if task_data.get("completed_at") else None)
        return new_task
