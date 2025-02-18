from fastapi import FastAPI

from api.controller import api_router

app = FastAPI()

app.include_router(api_router)
