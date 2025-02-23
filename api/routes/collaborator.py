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
    """
    Retorna uma lista de colaboradores.

    Args:
        skip (int): Número de registros a pular para paginação.
        limit (int): Número máximo de registros a retornar.

    Returns:
        list[Collaborator]: Lista de colaboradores cadastrados.
    """
    collaborators = await engine.find(
        Collaborator,
        skip=skip,
        limit=limit,
        sort=Collaborator.name
        )
    return collaborators


@router.get("/search",
            response_model=list[Collaborator],
            status_code=status.HTTP_200_OK)
async def find_collaborator_by_email(
    email: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100)
) -> list[Collaborator]:
    """
    Busca colaboradores pelo email.

    Args:
        email (str): Email do colaborador (busca parcial, case-insensitive).
        skip (int): Número de registros a pular para paginação.
        limit (int): Número máximo de registros a retornar.

    Returns:
        list[Collaborator]: Lista de colaboradores encontrados.

    Raises:
        HTTPException: 404 se nenhum colaborador for encontrado.
    """
    collaborators = await engine.find(
        Collaborator,
        {"email": {"$regex": f"{email}", "$options": "i"}},
        skip=skip,
        limit=limit,
        sort=Collaborator.name
    )
    if not collaborators:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborators not found.")
    return collaborators


@router.get("/{collaborator_id}",
            response_model=Collaborator,
            status_code=status.HTTP_200_OK)
async def find_by_id(collaborator_id: str) -> Collaborator:
    """
    Busca um colaborador pelo ID.

    Args:
        collaborator_id (str): ID do colaborador.

    Returns:
        Collaborator: Objeto do colaborador encontrado.

    Raises:
        HTTPException: 404 se o colaborador não for encontrado.
    """
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
    """
    Adiciona um colaborador a uma tarefa dentro de um projeto.

    Args:
        collaborator_id (str): ID do colaborador.
        project_id (str): ID do projeto.
        task_id (str): ID da tarefa.

    Returns:
        Task: Objeto da tarefa atualizada.

    Raises:
        HTTPException: 404 se o projeto, a tarefa ou o colaborador não forem encontrados.
        HTTPException: 400 se o colaborador já estiver associado à tarefa.
    """
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
    """
    Cria um novo colaborador.

    Args:
        collaborator (Collaborator): Dados do colaborador.

    Returns:
        Collaborator: Objeto do colaborador criado.

    Raises:
        HTTPException: 400 se um colaborador com o mesmo email já existir.
    """
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
    """
    Atualiza um colaborador pelo ID.

    Args:
        collaborator_id (str): ID do colaborador.
        collaborator_data (Collaborator): Dados atualizados.

    Returns:
        Collaborator: Objeto do colaborador atualizado.

    Raises:
        HTTPException: 404 se o colaborador não for encontrado.
    """
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
    """
    Remove um colaborador pelo ID.

    Args:
        collaborator_id (str): ID do colaborador.

    Returns:
        None

    Raises:
        HTTPException: 404 se o colaborador não for encontrado.
    """
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
        )
    if not collaborator:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Collaborator not found.")
    await engine.delete(collaborator)
    return
