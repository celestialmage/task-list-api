import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from typing import Optional
from ..db import db

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=True, default=None)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }

        if self.completed_at:
            task_dict["is_complete"] = True
        else:
            task_dict["is_complete"] = False

        if self.goal_id:
            task_dict["goal_id"] = self.goal_id

        return task_dict
    
    @classmethod
    def from_dict(cls, task_data):
        new_task = Task(title=task_data["title"], 
                        description=task_data["description"], 
                        completed_at=task_data["completed_at"] if task_data.get("completed_at") else None)
        return new_task
