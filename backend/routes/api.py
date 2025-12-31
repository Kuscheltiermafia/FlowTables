from fastapi import APIRouter
from backend.routes.api_routes import users, dev


api_router = APIRouter(prefix="/api", tags=["api"])

api_router.include_router(users.router)
api_router.include_router(dev.router)