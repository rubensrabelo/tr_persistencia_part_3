from fastapi import APIRouter, HTTPException, Query
from odmantic import ObjectId
from starlette import status

from database import get_engine
from models import Collaborator, Project, Task

router = APIRouter()

engine = get_engine()


@router.get("/",
            response_model=list[Collaborator],
            status_code=status.HTTP_200_OK)
async def find_all(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100)
) -> list[Collaborator]:
    collaborators = await engine.find(Collaborator, skip=skip, limit=limit)
    return collaborators


@router.get("/{collaborator_id}",
            response_model=Collaborator,
            status_code=status.HTTP_200_OK)
async def find_by_id(collaborator_id: str) -> Collaborator:
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
    )

    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found.")
    return collaborator


@router.get("/{collaborator_id}/project/{project_id}/task/{task_id}",
            response_model=Task,
            status_code=status.HTTP_200_OK)
async def add_collaborator_in_task(
    collaborator_id: str,
    project_id: str,
    task_id: str
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
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
    )
    if not collaborator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found.")
    if collaborator.id not in [c.id for c in task.collaborators]:
        task.collaborators.append(collaborator)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collaborator already associated with this task"
        )
    await engine.save(project)
    return task


@router.post("/",
             response_model=Collaborator,
             status_code=status.HTTP_201_CREATED)
async def create(collaborator: Collaborator) -> Collaborator:
    existing_collaborator = await engine.find_one(
        Collaborator, Collaborator.email == collaborator.email
    )
    if existing_collaborator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collaborator with this email already exists."
        )
    await engine.save(collaborator)
    return collaborator


@router.put("/{collaborator_id}",
            response_model=Collaborator,
            status_code=status.HTTP_200_OK)
async def update(collaborator_id: str,
                 collaborator_data: Collaborator) -> Collaborator:
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
        )
    if not collaborator:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Collaborator not found.")
    for key, value in collaborator_data.model_dump(exclude_unset=True).items():
        setattr(collaborator, key, value)
    await engine.save(collaborator)
    return collaborator


@router.delete("/{collaborator_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(collaborator_id: str) -> None:
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
        )
    if not collaborator:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Collaborator not found.")
    await engine.delete(collaborator)
    return
