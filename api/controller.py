from fastapi import APIRouter

from .routes.project import router as project_router
from .routes.task import router as task_router
from .routes.collaborator import router as collaborator_router

api_router = APIRouter()

api_router.include_router(
    project_router,
    prefix="/projects",
    tags=["Project"]
)
api_router.include_router(
    task_router,
    prefix="/tasks",
    tags=["Task"]
)
api_router.include_router(
    collaborator_router,
    prefix="/collaboratos",
    tags=["Collaborator"]
    )
