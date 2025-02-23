from fastapi import APIRouter, HTTPException, Query
from odmantic import ObjectId
from starlette import status
from datetime import datetime, timezone

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
    """
    Retorna uma lista de projetos.

    Args:
        skip (int): Número de registros a pular para paginação.
        limit (int): Número máximo de registros a retornar.

    Returns:
        list[Project]: Lista de projetos cadastrados.
    """
    projects = await engine.find(
        Project,
        skip=skip,
        limit=limit,
        sort=Project.created_at
        )
    return projects


@router.get("/search",
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def find_project_by_name(
        name: str,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=5, le=100)
) -> list[Project]:
    """
    Busca projetos pelo nome.

    Args:
        name (str): Nome do projeto (busca parcial, case-insensitive).
        skip (int): Número de registros a pular para paginação.
        limit (int): Número máximo de registros a retornar.

    Returns:
        list[Project]: Lista de projetos encontrados.

    Raises:
        HTTPException: 404 se nenhum projeto for encontrado.
    """
    projects = await engine.find(
        Project,
        {"name": {"$regex": f"{name}", "$options": "i"}},
        skip=skip,
        limit=limit,
        sort=Project.created_at
    )
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    return projects


@router.get("/{project_id}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def find_by_id(project_id: str) -> Project:
    """
    Busca um projeto pelo ID.

    Args:
        project_id (str): ID do projeto.

    Returns:
        Project: Objeto do projeto encontrado.

    Raises:
        HTTPException: 404 se o projeto não for encontrado.
    """
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
    """
    Cria um novo projeto.

    Args:
        project (Project): Dados do projeto.

    Returns:
        Project: Objeto do projeto criado.
    """
    await engine.save(project)
    return project


@router.put("/{project_id}",
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update(project_id: str,
                 project_data: Project) -> Project:
    """
    Atualiza um projeto pelo ID.

    Args:
        project_id (str): ID do projeto.
        project_data (Project): Dados atualizados do projeto.

    Returns:
        Project: Objeto do projeto atualizado.

    Raises:
        HTTPException: 404 se o projeto não for encontrado.
    """
    project = await engine.find_one(
        Project, Project.id == ObjectId(project_id)
    )
    if not project:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.updated_at = datetime.now(timezone.utc)
    await engine.save(project)
    return project


@router.delete("/{project_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: str) -> None:
    """
    Remove um projeto pelo ID.

    Args:
        project_id (str): ID do projeto.

    Returns:
        None

    Raises:
        HTTPException: 404 se o projeto não for encontrado.
    """
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
