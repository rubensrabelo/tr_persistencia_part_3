from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from starlette import status
from database import get_engine
from models import Project

router = APIRouter()
engine = get_engine()


@router.get("/total/project",
            response_model=dict,
            status_code=status.HTTP_200_OK)
async def total_projects() -> dict:
    """
    Obtém o número total de projetos cadastrados no banco de dados.

    Returns:
        dict: Um dicionário contendo o total de projetos no formato:
        {
            "total_projects": int
        }
    """
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
    """
    Retorna o número total de tarefas dentro de cada projeto.

    Args:
        min_tasks (int, opcional): Número mínimo de tarefas por projeto. Default = 0.
        max_tasks (int, opcional): Número máximo de tarefas por projeto.
        limit (int, opcional): Número máximo de projetos retornados. Default = 10.
        skip (int, opcional): Número de projetos a serem ignorados no início da lista. Default = 0.

    Returns:
        list[dict]: Lista de dicionários contendo o nome do projeto e o total de tarefas.
    """
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


@router.get("/total/collaborators/by/task/{project_id}",
            response_model=list[dict],
            status_code=status.HTTP_200_OK)
async def total_collaborators_by_task(
    project_id: str,
    min_collaborators: int = Query(0, alias="min"),
    max_collaborators: int = Query(None, alias="max"),
    limit: int = Query(10),
    skip: int = Query(0)
) -> list[dict]:
    """
    Obtém a quantidade de colaboradores por tarefa dentro de um projeto específico.

    Args:
        project_id (str): ID do projeto cujas tarefas serão analisadas.
        min_collaborators (int, opcional): Número mínimo de colaboradores por tarefa. Default = 0.
        max_collaborators (int, opcional): Número máximo de colaboradores por tarefa.
        limit (int, opcional): Número máximo de resultados retornados. Default = 10.
        skip (int, opcional): Número de tarefas a serem ignoradas no início da lista. Default = 0.

    Returns:
        list[dict]: Lista de dicionários contendo o ID da tarefa, nome da tarefa e total de colaboradores.

    Raises:
        HTTPException: 404 se o projeto não for encontrado.
    """
    collection = engine.get_collection(Project)

    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
        )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    pipeline = [
        {"$match": {"_id": ObjectId(project_id)}},
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
    """
    Obtém o número total de tarefas atribuídas a cada colaborador.

    Args:
        min_tasks (int, opcional): Número mínimo de tarefas por colaborador. Default = 0.
        max_tasks (int, opcional): Número máximo de tarefas por colaborador.
        limit (int, opcional): Número máximo de resultados retornados. Default = 10.
        skip (int, opcional): Número de colaboradores a serem ignorados no início da lista. Default = 0.

    Returns:
        list[dict]: Lista de dicionários contendo o nome do colaborador, e-mail e total de tarefas.
    """
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
