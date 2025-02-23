from fastapi import APIRouter, Query
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
    return {"total_projects": total_projects}


@router.get("/total/tasks/by/project",
            response_model=list[dict],
            status_code=status.HTTP_200_OK)
async def total_tasks_by_project(
    min_tasks: int = Query(0, alias="min"),
    max_tasks: int = Query(None, alias="max"),
    limit: int = Query(10),
    skip: int = Query(0)
) -> list[dict]:
    collection = engine.get_collection(Project)

    pipeline = [
        {"$project": {
            "_id": {"$toString": "$_id"},
            "project_name": "$name",
            "total_tasks": {"$size": {"$ifNull": ["$tasks", []]}}
        }},
        {"$match": {
            "total_tasks": {
                "$gte": min_tasks,
                **({"$lte": max_tasks} if max_tasks is not None else {})
                }
        }},
        {"$sort": {"total_tasks": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)
    return results


@router.get("/total/collaborators/by/task",
            response_model=list[dict],
            status_code=status.HTTP_200_OK)
async def total_collaborators_by_task(
    min_collaborators: int = Query(0, alias="min"),
    max_collaborators: int = Query(None, alias="max"),
    limit: int = Query(10),
    skip: int = Query(0)
) -> list[dict]:
    collection = engine.get_collection(Project)

    pipeline = [
        {"$unwind": "$tasks"},
        {"$project": {
            "_id": 0,
            "task_id": {"$toString": "$tasks.id"},
            "task_name": "$tasks.name",
            "total_collaborators": {
                "$size": {"$ifNull": ["$tasks.collaborators", []]}
                }
        }},
        {"$match": {
            "total_collaborators": {
                "$gte": min_collaborators,
                **({
                    "$lte": max_collaborators}
                    if max_collaborators is not None else {})
                    }
        }},
        {"$sort": {"total_collaborators": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)
    return results


@router.get("/total/tasks/collaborator",
            response_model=list[dict],
            status_code=status.HTTP_200_OK)
async def total_tasks_by_collaborator(
    min_tasks: int = Query(0, alias="min"),
    max_tasks: int = Query(None, alias="max"),
    limit: int = Query(10),
    skip: int = Query(0)
) -> list[dict]:
    collection = engine.get_collection(Project)

    pipeline = [
        {"$unwind": "$tasks"},
        {"$unwind": "$tasks.collaborators"},
        {"$lookup": {
            "from": "collaborator",
            "localField": "tasks.collaborators.email",
            "foreignField": "email",
            "as": "collaborator_info"
        }},
        {"$unwind": "$collaborator_info"},
        {"$group": {
            "_id": {
                "name": "$collaborator_info.name",
                "email": "$collaborator_info.email"
            },
            "total_tasks": {"$sum": 1}
        }},
        {"$match": {
            "total_tasks": {
                "$gte": min_tasks,
                **({"$lte": max_tasks}if max_tasks is not None else {})
                }
        }},
        {"$project": {
            "_id": 0,
            "collaborator_name": "$_id.name",
            "collaborator_email": "$_id.email",
            "total_tasks": 1
        }},
        {"$sort": {"total_tasks": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)
    return results
