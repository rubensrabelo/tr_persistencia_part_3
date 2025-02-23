from fastapi import APIRouter
from starlette import status

from database import get_engine
from models import Project


router = APIRouter()
engine = get_engine()


@router.get("/total/project",
            response_model=dict,
            status_code=status.HTTP_200_OK)
async def total_projects() -> dict:
    total_projects = await engine.count(Project)
    return {
        "total projects": total_projects
    }


@router.get("/total/tasks/by/project")
async def total_tasks_by_project():
    collection = engine.get_collection(Project)

    pipeline = [
        {
            "$project": {
                "project_name": "$name",
                "total_tasks": {"$size": {"$ifNull": ["$tasks", []]}}
            }
        },
        {
            "$sort": {"total_tasks": -1}
        }
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)

    results = [
        {
            "_id": str(result["_id"]),
            "project_name": result["project_name"],
            "total_tasks": result["total_tasks"]
        }
        for result in results
    ]
    return results
