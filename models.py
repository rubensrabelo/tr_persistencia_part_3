from odmantic import Model, EmbeddedModel, Field
from bson import ObjectId
from enum import Enum
from datetime import datetime, timezone


class Collaborator(Model):
    name: str
    email: str = Field(unique=True)
    function: str


class StatusEnum(str, Enum):
    NOT_DONE = "Not done"
    DOING = "Doing"
    DONE = "Done"


class Task(EmbeddedModel):
    name: str
    description: str
    create_at: datetime = datetime.now(timezone.utc)
    update_at: datetime = datetime.now(timezone.utc)
    status: StatusEnum = StatusEnum.NOT_DONE
    collaborator: list[ObjectId] = []


class Project(Model):
    name: str
    description: str
    create_at: datetime = datetime.now(timezone.utc)
    update_at: datetime = datetime.now(timezone.utc)
    status: StatusEnum = StatusEnum.NOT_DONE
    tasks: list[Task] = []
