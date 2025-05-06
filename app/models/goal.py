from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[Optional["Task"]] = relationship(back_populates="goals")

    def to_dict(self):
        goal_as_dict = {
            "id": self.id,
            "title": self.title
        }

        if self.task:
            goal_as_dict["task"] = self.task.title

        return goal_as_dict
    
    @classmethod
    def from_dict(cls, goal_data):
        new_goal = Goal(title=goal_data["title"])

        if goal_data.get("task_id"):
            new_goal.task_id = goal_data["task_id"]

        return new_goal