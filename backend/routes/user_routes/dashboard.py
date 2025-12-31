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

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard_get(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "cache_buster": int(time.time())} 
    )