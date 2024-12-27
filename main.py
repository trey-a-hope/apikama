# FastAPI application for integrating with Nakama game servers
# Author: Trey Hope
# Created: December 2024

from typing import List
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models.requests.email_create_request import EmailCreateRequest
from models.requests.leaderboard_create_request import LeaderboardCreateRequest
from models.responses.authenticate_email_response import AuthenticateEmailResponse
from models.requests.email_auth_request import EmailAuthRequest
from enum import Enum
from models.responses.get_account_response import GetAccountResponse
from models.responses.leaderboard_record_response import LeaderboardRecordResponse

from models.responses.leaderboard_response import LeaderboardResponse
from services.account_service import AccountService
from services.auth_service import AuthService
from services.leaderboard_service import LeaderboardService

# Command to run the server with hot reload
# uvicorn main:app --reload

# Server configuration
local_host = "127.0.0.1"  # Local development server
prod_host = "24.144.85.68"  # Production server IP

# 24.144.85.68:7350:0:defaultkey
# 127.0.0.1:7350:0:defaultkey

# Server connection string format: host:port:ssl:key
server_string = f"{prod_host}:7350:0:defaultkey"

# Application metadata
_title: str = "Apikama"
_description: str = (
    f"A high-performance FastAPI service that seamlessly integrates with Nakama game servers."
)

# Initialize Jinja2 templating engine
templates: Jinja2Templates = Jinja2Templates(
    directory="templates",
)

# Initialize FastAPI application with metadata and documentation endpoints
app: FastAPI = FastAPI(
    title=_title,
    description=_description,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
)

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files directory for serving static assets
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# Dependency injection providers
def get_account_deps() -> AccountService:
    """Provides AccountService instance for dependency injection"""
    return AccountService()


def get_auth_deps() -> AuthService:
    """Provides AuthService instance for dependency injection"""
    return AuthService()


def get_leaderboard_deps() -> LeaderboardService:
    """Provides LeaderboardService instance for dependency injection"""
    return LeaderboardService()


# API endpoint tags for documentation organization
class ApiTag(Enum):
    ACOUNT = "Acount"
    AUTHENTICATION = ("Authentication",)
    LEADERBOARD = ("Leaderboard",)
    GENERAL = "General"


# Account endpoints
@app.get(
    "/getAccount",
    tags=[ApiTag.ACOUNT],
    description="Retrieves the user's account information.",
    response_model=GetAccountResponse,
    name="Get Account",
)
async def getAccount(
    server_string: str,  # Server connection details
    session_token: str,  # User's authentication token
    account: AccountService = Depends(get_account_deps),
):
    """Retrieves account information for an authenticated user"""
    return await account.get_account(server_string, session_token)


# Authentication endpoints
@app.post(
    "/loginEmail",
    tags=[ApiTag.AUTHENTICATION],
    description="Authenticates a user's email credentials against the server.",
    response_model=AuthenticateEmailResponse,
    name="Login Email",
)
async def loginEmail(
    server_string: str,  # Server connection details
    request: EmailAuthRequest,  # Email authentication request data
    auth: AuthService = Depends(get_auth_deps),
):
    """Authenticates a user's email credentials against the server."""
    return await auth.login_email(server_string, request)


@app.post(
    "/signupEmail",
    tags=[ApiTag.AUTHENTICATION],
    description="Create a new user via email credentials against the server.",
    response_model=AuthenticateEmailResponse,
    name="Signup Email",
)
async def signupEmail(
    server_string: str,  # Server connection details
    request: EmailCreateRequest,  # Email authentication request data
    auth: AuthService = Depends(get_auth_deps),
):
    """Create a new user via email credentials against the server."""
    return await auth.signup_email(server_string, request)


# General endpoints
@app.get("/", response_class=HTMLResponse, tags=[ApiTag.GENERAL])
async def default(request: Request):
    """Serves the main application landing page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,  # Required by Jinja2
            "title": _title,
            "description": _description,
        },
    )


# Leaderboard endpoints
@app.get(
    "/getLeaderboardRecords",
    tags=[ApiTag.LEADERBOARD],
    description="Retrieves leaderboard records.",
    response_model=LeaderboardResponse,
    name="Get Leaderboard Records",
)
async def getLeaderboardRecords(
    server_string: str,  # Server connection details
    session_token: str,  # User's authentication token
    leaderboard_id: str,
    leaderboard: LeaderboardService = Depends(get_leaderboard_deps),
):
    """Retrieves leaderboard records"""
    return await leaderboard.get_records(server_string, session_token, leaderboard_id)


@app.post(
    "/createLeaderboardRecord",
    tags=[ApiTag.LEADERBOARD],
    description="Creates a leaderboard record.",
    response_model=LeaderboardRecordResponse,
    name="Create Leaderboard Record",
)
async def createLeaderboardRecord(
    server_string: str,  # Server connection details
    session_token: str,  # User's authentication token
    leaderboard_id: str,
    request: LeaderboardCreateRequest,
    leaderboard: LeaderboardService = Depends(get_leaderboard_deps),
):
    """Retrieves leaderboard records"""
    return await leaderboard.create_record(
        server_string, session_token, leaderboard_id, request
    )
