from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import os
from backend.routes import api
from backend.data_management.pool_handler import init_data_pool, close_data_pool
from backend.user_management.pool_handler import init_user_pool, close_user_pool
from contextlib import asynccontextmanager 
import time
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup: Initializing database pools...")
    await init_data_pool()
    await init_user_pool()
    print("Application Startup: Database pools initialized successfully.")
    
    yield
    
    print("Application Shutdown: Closing connections...")
    await close_user_pool()
    await close_data_pool()



ERROR_DETAILS = {
    400: ("400", "Der Server konnte Ihre Anfrage aufgrund fehlerhafter Syntax oder ungültiger Daten nicht verarbeiten. Bitte korrigieren Sie die Anfrage."),
    401: ("401", "Für diese Aktion ist eine gültige Authentifizierung (Zugangsdaten) erforderlich. Bitte melden Sie sich an."),
    403: ("403", "Sie sind authentifiziert, haben aber nicht die notwendigen Berechtigungen, um auf diese Ressource zuzugreifen."),
    404: ("404", "Die von Ihnen angeforderte Adresse oder Ressource konnte nicht gefunden werden. Überprüfen Sie bitte die URL."),
    405: ("405", "Die verwendete HTTP-Methode (z.B. GET, POST) ist für diesen Endpunkt unzulässig."),
    422: ("422", "Die Anfrage ist syntaktisch korrekt, aber semantisch fehlerhaft (häufig bei Validierungsfehlern in FastAPI)."),
    429: ("429", "Sie haben zu viele Anfragen in kurzer Zeit gesendet. Bitte warten Sie einen Augenblick, bevor Sie es erneut versuchen."),
    500: ("500", "Ein unerwarteter Fehler ist auf dem Server aufgetreten. Das Problem wird untersucht und behoben."),
    503: ("503", "Der Dienst ist momentan wegen Wartungsarbeiten oder Überlastung nicht erreichbar. Bitte versuchen Sie es später erneut."),
    504: ("504", "Der Server hat von einem vorgeschalteten Dienst keine rechtzeitige Antwort erhalten."),
}

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api.api_router)

templates = Jinja2Templates(directory="templates")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):

    status_code = exc.status_code
    
    # 1. Titel und Standardbeschreibung abrufen
    title, description = ERROR_DETAILS.get(
        status_code, 
        (f"Fehler {status_code}", f"Ein allgemeiner Fehlercode ({status_code}) wurde vom Server zurückgegeben.")
    )
    
    # 2. Detail-Nachricht verwenden, falls in der HTTPException gesetzt
    final_description = f"{description} ({exc.detail})"

    # 3. Template rendern und den korrekten Statuscode zurückgeben
    return templates.TemplateResponse(
        "error.html", # Der Pfad im "templates/" Ordner
        {
            "request": request, 
            "STATUS_CODE": str(status_code), 
            "TITLE": title, 
            "DESCRIPTION": final_description
        },
        status_code=status_code # WICHTIG: Setzt den HTTP-Statuscode der Antwort
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "cache_buster": int(time.time())} 
    )

@app.get("/favicon")

@app.get("/tests", response_class=HTMLResponse)
async def tests_url(request: Request):
    return templates.TemplateResponse(
        "tests.html",
        {"request": request, "cache_buster": int(time.time())} 
    )


@app.get("/secret")
def read_secret_data():
    """Example route that raises a 403 Forbidden error."""
    # This will trigger the custom exception handler above
    raise HTTPException(status_code=403, detail="Kein Zugriff. Nur Administratoren dürfen diesen Bereich sehen.")

@app.get("/trigger-404")
def trigger_404_programmatically():
    """Example route that raises a 404 Not Found error."""
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Der angeforderte API-Endpunkt ist nicht vorhanden.")