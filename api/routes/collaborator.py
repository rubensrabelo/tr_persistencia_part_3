from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from odmantic import ObjectId
from starlette import status

from models import Collaborator

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


@router.post("/",
             response_model=Collaborator,
             status_code=status.HTTP_201_CREATED)
async def create(collaborator: Collaborator) -> Collaborator:
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
    if not collaborator_id:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Collaborator not found.")
    for key, value in collaborator_data.items():
        setattr(collaborator, key, value)
    await engine.save(collaborator)
    return collaborator


@router.delete("/{collaborator_id}",
               response_model=Collaborator,
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(collaborator_id: str) -> dict:
    collaborator = await engine.find_one(
        Collaborator, Collaborator.id == ObjectId(collaborator_id)
        )
    if not collaborator:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                            detail="Collaborator not found.")
    await engine.delete(collaborator)
    return {"message": "Collaborator deleted."}
