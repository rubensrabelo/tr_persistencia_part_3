from odmantic import Model, EmbeddedModel
from bson import ObjectId
from enum import Enum
from datetime import datetime, timezone


class Collaborator(Model):
    name: str
    email: str
    function: str


class StatusEnum(str, Enum):
    NOT_DONE = "Not done"
    DOING = "Doing"
    DONE = "Done"


class Task(EmbeddedModel):
    name: str
    description: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    status: StatusEnum = StatusEnum.NOT_DONE
    collaborators: list[ObjectId] = []


class Project(Model):
    name: str
    description: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    status: StatusEnum = StatusEnum.NOT_DONE
    tasks: list[Task] = []
