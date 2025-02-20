from fastapi import APIRouter

from .routes.collaborator import router as collaborator_router

api_router = APIRouter()

api_router.include_router(collaborator_router,
                          prefix="/collaboratos",
                          tags=["Collaborator"]
                          )
