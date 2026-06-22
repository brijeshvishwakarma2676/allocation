import logging
import platform
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, Base
from app.routers import projects, allocation, admin, cancellation, customers


# ─── Logging ─────────────────────────────────────────────────────────────────

class ArchiveRotatingFileHandler(RotatingFileHandler):
    LOG_TIMESTAMP_FORMATS = ("%Y-%m-%d %H:%M:%S,%f", "%Y-%m-%d %H:%M:%S")

    def __init__(self, filename, archive_dir=None, **kwargs):
        self.archive_dir = Path(archive_dir or Path(filename).parent / "log_archive")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(filename=filename, **kwargs)
        self.current_period_start = self._resolve_period_start(Path(self.baseFilename))

    def _format_timestamp(self, value: datetime) -> str:
        return value.strftime("%Y%m%d_%H%M%S")

    def _read_first_log_timestamp(self, source: Path):
        try:
            with source.open("r", encoding=self.encoding or "utf-8", errors="ignore") as f:
                first_line = f.readline().strip()
        except OSError:
            return None
        if not first_line:
            return None
        timestamp_text = first_line.split(" - ", 1)[0]
        for fmt in self.LOG_TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(timestamp_text, fmt)
            except ValueError:
                continue
        return None

    def _resolve_period_start(self, source: Path) -> datetime:
        if source.exists() and source.stat().st_size > 0:
            return self._read_first_log_timestamp(source) or datetime.fromtimestamp(source.stat().st_mtime)
        return datetime.now()

    def _next_archive_file(self, source: Path, period_start: datetime, period_end: datetime) -> Path:
        suffix = f"_{source.name}"
        max_index = 0
        for archived_file in self.archive_dir.glob(f"*{suffix}"):
            prefix = archived_file.name.split("_", 1)[0]
            if prefix.isdigit():
                max_index = max(max_index, int(prefix))
        start_label = self._format_timestamp(period_start)
        end_label = self._format_timestamp(period_end)
        return self.archive_dir / f"{max_index + 1}_{start_label}_to_{end_label}_{source.name}"

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        source = Path(self.baseFilename)
        if source.exists() and source.stat().st_size > 0:
            period_start = self.current_period_start or self._resolve_period_start(source)
            period_end = datetime.fromtimestamp(source.stat().st_mtime)
            archive_file = self._next_archive_file(source, period_start, period_end)
            self.rotate(str(source), str(archive_file))
        self.current_period_start = datetime.now()
        if not self.delay:
            self.stream = self._open()


def configure_logging() -> None:
    log_file = Path(settings.APP_LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    archive_dir = Path(settings.APP_LOG_ARCHIVE_DIR)
    archive_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
        handlers=[
            ArchiveRotatingFileHandler(
                filename=log_file,
                archive_dir=archive_dir,
                maxBytes=settings.APP_LOG_MAX_BYTES,
                backupCount=0,
                encoding="utf-8",
            )
        ],
        force=True,
    )


configure_logging()
logger = logging.getLogger(__name__)

# ─── DB Tables ───────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/api/allocation/docs",
    redoc_url="/api/allocation/redoc",
    openapi_url="/api/allocation/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router,     prefix="/api/allocation")
app.include_router(allocation.router,   prefix="/api/allocation")
app.include_router(admin.router,        prefix="/api/allocation")
app.include_router(cancellation.router, prefix="/api/allocation")
app.include_router(customers.router,    prefix="/api/allocation")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/api/allocation/docs")


# ─── Exception Handlers ───────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTPException %s: %s — %s %s", exc.status_code, exc.detail, request.method, request.url)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": " -> ".join(str(l) for l in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    logger.error("ValidationError %s %s: %s", request.method, request.url, errors)
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Validation failed", "details": errors},
    )

@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    msg = f"Missing required field: {exc}"
    logger.error("KeyError %s %s: %s", request.method, request.url, msg)
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": msg},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("DatabaseError %s %s: %s", request.method, request.url, str(exc))
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": "Database error. Please try again."},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception %s %s: %s", request.method, request.url, str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected error occurred."},
    )


# ─── Entry Point ─────────────────────────────────────────────────────────────

def startup():
    print(f"[{settings.APP_NAME} v{settings.VERSION}] Application started on port {settings.PORT}")

def shutdown():
    print(f"[{settings.APP_NAME}] Application shutdown")

if __name__ == "__main__":
    if platform.system() != "Linux":
        try:
            from gunicorn.app.wsgiapp import WSGIApplication

            class StandaloneApplication(WSGIApplication):
                def __init__(self, app_uri, options=None):
                    self.options = options or {}
                    self.app_uri = app_uri
                    super().__init__()

                def load_config(self):
                    config = {
                        key: value
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    }
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

            options = {
                "bind": f"0.0.0.0:{settings.PORT}",
                "workers": 8,
                "threads": 2,
                "worker_class": "uvicorn.workers.UvicornH11Worker",
                "timeout": 120,
                "keepalive": 10,
                "max_requests": 1000,
                "max_requests_jitter": 200,
                "graceful_timeout": 30,
                "limit_request_line": 8190,
            }
            StandaloneApplication("main:app", options).run()

        except ImportError:
            uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
    else:
        uvicorn.run(
            app="main:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=not settings.IS_PROD,
        )
