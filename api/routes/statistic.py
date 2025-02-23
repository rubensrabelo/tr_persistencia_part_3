from fastapi import APIRouter
from starlette import status

from database import get_engine
from database import Project


router = APIRouter()
engine = get_engine()


@router.get("/count/total/project",
            response_model=dict,
            status_code=status.HTTP_200_OK)
async def count_projects() -> dict:
    total_projects = await engine.count(Project)
    return {
        "total projects": total_projects
    }
