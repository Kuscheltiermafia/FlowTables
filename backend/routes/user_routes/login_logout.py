# START STANDARD IMPORT
from fastapi import FastAPI, Request, HTTPException, APIRouter, Form, Depends
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from dataclasses import dataclass
import time
from backend.user_management.pool_handler import user_pool, get_user_pool
from backend.user_management.user_handler import *
from starlette.middleware.sessions import SessionMiddleware
templates = Jinja2Templates(directory="templates")
# END STANDARD IMPORT

router = APIRouter(tags=["login_logout"])


@router.get("/login", response_class=HTMLResponse)
async def user_login_get_route(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "cache_buster": int(time.time())} 
    )
    
@router.post("/login")
async def user_login_post_route(request: Request, username: str, password: str, conn: Connection = Depends(get_user_pool)):
    user_id = None
    user_valid = valid_password(user_connection=conn, userKey=username, password=password)
    if user_valid:
        user_id = get_user_by_username(username)
        request.session["logged_in"] = True
        request.session["user"] = user_id

    return {"id": user_id}

@router.post("/logout")
async def user_logout_post_route(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@router.get("/logout", response_class=HTMLResponse)
async def user_logout_get_route(request: Request):
    request.session.clear()
    return 'window.location("/?message=logged_out");'