from fastapi import APIRouter, Form, Depends
from dataclasses import dataclass

from backend.user_management.pool_handler import get_user_pool
from backend.user_management.user_handler import *


router = APIRouter(prefix="/users", tags=["users"])

@dataclass
class User:
    userName: str
    firstName: str
    lastName: str
    email: str
    password: str

@router.post("/create_user")
async def create_user_post(
    userName: str = Form(...),
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    conn: Connection = Depends(get_user_pool)
):
    user = User(userName, firstName, lastName, email, password)
    usr_id = await create_user(conn, userName, firstName, lastName, email, password)
    print(usr_id)
    return {"created_user": user.__dict__}