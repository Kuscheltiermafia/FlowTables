from fastapi import APIRouter
from backend.routes.user_routes import login_logout


user_router = APIRouter(tags=["user"])

user_router.include_router(login_logout.router)