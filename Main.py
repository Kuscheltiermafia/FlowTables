import logging.config
import os
import sys
import uuid
import time
from contextlib import asynccontextmanager

from rich.logging import RichHandler
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from backend.data_management.pool_handler import init_data_pool, close_data_pool
from backend.routes import api, user
from backend.user_management.pool_handler import init_user_pool, close_user_pool


# -- Logging Configuration --

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def get_logging_config(env: str = "development"):
    log_dir = "logs"
    log_file = os.path.join(log_dir, "app.log")
    
    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(lineno)d %(pathname)s",
            },
            "rich": {"format": "%(message)s", "datefmt": "[%X]"},
            "file": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 3,
                "formatter": "json" if env == "production" else "file",
                "level": LOG_LEVEL,
            }
        },
        "loggers": {
            "": {"level": LOG_LEVEL, "handlers": ["file"], "propagate": False},
            "uvicorn.error": {"level": "INFO", "handlers": ["file"], "propagate": False},
            "uvicorn.access": {"level": "WARNING", "handlers": ["file"], "propagate": False},
        },
    }

    if env != "production":
        # Add rich console output for development, in addition to the file log
        config["handlers"]["console"] = {
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "level": LOG_LEVEL,
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
        }
        config["loggers"][""]["handlers"].append("console")
        config["loggers"]["uvicorn.error"]["handlers"].append("console")

    return config

def setup_logging(env: str = "development"):
    config = get_logging_config(env)
    logging.config.dictConfig(config)


# -- Application Setup --

APP_ENV = os.getenv("APP_ENV", "development")
setup_logging(APP_ENV)

logger = logging.getLogger("api_logger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application Startup: Initializing database pools...")
    try:
        await init_data_pool()
        await init_user_pool()
        logger.info("Application Startup: Database pools initialized successfully.")
    except Exception as e:
        logger.critical("Application Startup Failed: Could not initialize database pools.", exc_info=True)
    
    yield
    
    logger.info("Application Shutdown: Closing database connections...")
    try:
        await close_user_pool()
        await close_data_pool()
        logger.info("Application Shutdown: Database connections closed successfully.")
    except Exception as e:
        logger.error("Application Shutdown Error: Could not close database pools cleanly.", exc_info=True)



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

# Routers
app.include_router(api.api_router)
app.include_router(user.user_router)

load_dotenv('.env.deployment')
SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def professional_logging_middleware(request: Request, call_next):
    # Bypass logging for static files
    if request.url.path.startswith("/static"):
        return await call_next(request)

    start_time = time.time()
    request_id = str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID", request_id)

    # Prepare a dictionary with structured request data
    log_dict = {
        "request_id": request_id,
        "correlation_id": correlation_id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        "http": {
            "request": {
                "method": request.method,
                "url": str(request.url),
                "headers": {k: v for k, v in request.headers.items() if k.lower() not in ["authorization", "cookie"]},
                "client_ip": request.client.host if request.client else "unknown",
            }
        },
        "event": {"kind": "event", "category": "web", "type": "start"},
    }

    logger.info(f"Request started: {request.method} {request.url}", extra=log_dict)

    response = None
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        status_code = response.status_code

        log_dict["http"]["response"] = {
            "status_code": status_code,
            "headers": {k: v for k, v in response.headers.items()},
        }
        log_dict["event"]["duration"] = process_time
        log_dict["event"]["outcome"] = "success" if status_code < 400 else "failure"
        log_dict["event"]["type"] = "end"

        if status_code >= 500:
            logger.error(f"Request finished with error: {request.method} {request.url}", extra=log_dict)
        elif status_code >= 400:
            logger.warning(f"Request finished with client error: {request.method} {request.url}", extra=log_dict)
        else:
            logger.info(f"Request finished successfully: {request.method} {request.url}", extra=log_dict)

        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = correlation_id

    except Exception as e:
        process_time = time.time() - start_time
        
        # Log the exception with a full traceback
        log_dict["event"]["outcome"] = "failure"
        log_dict["event"]["duration"] = process_time
        log_dict["event"]["type"] = "end"
        
        logger.critical(
            f"Unhandled exception: {request.method} {request.url}",
            exc_info=True, # This adds the traceback
            extra=log_dict
        )

        # Re-raise to be handled by FastAPI's default handler,
        # which will then be caught by our custom exception handler below if it's a StarletteHTTPException
        # or result in a 500 error.
        if not response:
            response = Response("Internal Server Error", status_code=500)

    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):

    status_code = exc.status_code
    
    title, description = ERROR_DETAILS.get(
        status_code, 
        (f"{status_code}", f"Ein allgemeiner Fehlercode ({status_code}) wurde vom Server zurückgegeben.")
    )
    
    final_description = f"{description} ({exc.detail})"

    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "STATUS_CODE": str(status_code), 
            "TITLE": title, 
            "DESCRIPTION": final_description
        },
        status_code=status_code 
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, message: str = "null"):
    if "logged_in" in request.session and request.session["logged_in"] == True:
        logg_status = "true"
    else:
        logg_status = "false"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "cache_buster": int(time.time()), "message": message, "logg_status": logg_status} 
    )



@app.get("/secret")
def read_secret_data():
    """Example route that raises a 403 Forbidden error."""
    # This will trigger the custom exception handler above
    raise HTTPException(status_code=403, detail="Kein Zugriff. Nur Administratoren dürfen diesen Bereich sehen.")

@app.get("/trigger-500")
def trigger_500_programmatically():
    """Example route that raises a 404 Not Found error."""
    raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting uvicorn server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.critical(f"Failed to start uvicorn server: {e}", exc_info=True)
        sys.exit(1)
