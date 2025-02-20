from fastapi import APIRouter, HTTPException, Query
from odmantic import ObjectId
from starlette import status

from database import get_engine
from models import Project

router = APIRouter()

engine = get_engine()


@router.get("/",
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def find_all(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100)
) -> list[Project]:
    projects = await engine.find(Project, skip=skip, limit=limit)
    return projects


@router.get("/{project_id}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def find_by_id(project_id: str) -> Project:
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    return project


@router.post("/",
             response_model=Project,
             status_code=status.HTTP_201_CREATED)
async def create(project: Project) -> Project:
    await engine.save(project)
    return project


@router.put("/{project_id}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update(project_id: int,
                 project_data: Project) -> Project:
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    await engine.save(project)
    return project


@router.delete("/{project_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: int) -> None:
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    await engine.delete(project)
    return
