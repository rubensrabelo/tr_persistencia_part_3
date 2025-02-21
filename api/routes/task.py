from fastapi import APIRouter, HTTPException
from odmantic import ObjectId
from starlette import status
from datetime import datetime, timezone

from database import get_engine
from models import Project, Task

router = APIRouter()

engine = get_engine()


@router.get("/{task_id}/project/{project_id}",
            response_model=Task,
            status_code=status.HTTP_200_OK)
async def find_by_id(
    task_id: str,
    project_id: str
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
    task = next(
        (
            task for task in project.tasks
            if task.id == ObjectId(task_id)
        ),
        None
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
            )
    return task


@router.post("/project/{project_id}",
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


@router.put("/{task_id}/project/{project_id}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update(
    task_id: str,
    project_id: str,
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
    task = next(
        (task for task in project.tasks if task.id == ObjectId(task_id)), None
        )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    task_data.updated_at = datetime.now(timezone.utc)
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await engine.save(project)
    return project


@router.delete("/{task_id}/project/{project_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    task_id: str,
    project_id: str
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
    project.tasks = [
        task
        for task in project.tasks
        if task.id != ObjectId(task_id)
    ]
    await engine.save(project)
    return
