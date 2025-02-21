from fastapi import APIRouter, HTTPException
from odmantic import ObjectId
from starlette import status
from datetime import datetime, timezone

from database import get_engine
from models import Project, Task

router = APIRouter()

engine = get_engine()


@router.get("/{project_id}/{task_position}",
            response_model=Task,
            status_code=status.HTTP_200_OK)
async def find_by_id(
    project_id: str,
    task_position: int
) -> Task:
    project = await engine.find_one(
        Project,
        Project.id == ObjectId(project_id)
        )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
            )
    if task_position < 0 or task_position >= len(project.tasks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
            )
    return project.tasks[task_position]


@router.post("/{project_id}",
             response_model=Project,
             status_code=status.HTTP_201_CREATED)
async def create(
    project_id: str,
    task: Task
) -> Project:
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
        )
    if not project:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")
    project.tasks.append(task)
    await engine.save(project)
    return project


@router.put("/{project_id}/{task_position}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update(
    project_id: str,
    task_position: int,
    task_data: Task
):
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if task_position < 0 or task_position >= len(project.tasks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    task_data.updated_at = datetime.now(timezone.utc)
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(project.tasks[task_position], key, value)
    await engine.save(project)
    return project


@router.delete("/{project_id}/{task_position}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    project_id: str,
    task_position: int
) -> None:
    project = await engine.find_one(
        Project,
        Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if task_position < 0 or task_position >= len(project.tasks):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    project.tasks.pop(task_position)
    await engine.save(project)
    return
