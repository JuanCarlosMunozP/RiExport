import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from api import auth
from db.session import create_tables_if_not_exist

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing database tables...")
    create_tables_if_not_exist()
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    raise

app = FastAPI(
    title="RiEXport",
    description="API for app for export coffee and cacaos",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)


@app.get("/")
async def root():
    return {
        "message":"Welcome to the RiExport API",
        "docs_urls":"/docs",
        "version":"1.0.0"
    }

@app.get("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")