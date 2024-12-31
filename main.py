# FastAPI application for integrating with Nakama game servers
# Author: Trey Hope
# Created: December 2024

from typing import Optional
from fastapi import Body, Depends, FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from enums.api_tag import ApiTag
from enums.ssl_option import SSLOption
from models.account import Account
from models.requests.leaderboard_create_request import LeaderboardCreateRequest
from models.session import Session
from models.requests.email_auth_request import AccountEmail
from models.responses.delete_account_response import DeleteAccountResponse
from models.responses.leaderboard_record_response import LeaderboardRecordResponse
from models.responses.leaderboard_response import LeaderboardResponse
from models.responses.update_account_response import UpdateAccountResponse
from services.account_service import (
    AccountService,
    UpdateAccountRequest,
)
from services.encription_service import EncryptionService
from services.leaderboard_service import LeaderboardService
from static.api_descriptions import ApiDescriptions

# Command to run the server with hot reload
# uvicorn main:app --reload

# NOTE: apikama-prod cannot use the local game server.

is_dev_mode = True

_title: str = "Apikama"

# Initialize Jinja2 templating engine
templates: Jinja2Templates = Jinja2Templates(
    directory="templates",
)

# Initialize FastAPI application with metadata and documentation endpoints
app = FastAPI(
    title=_title,
    description=ApiDescriptions.APP,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
    swagger_ui_parameters={"docExpansion": "none"},
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


# def get_auth_deps() -> AuthService:
#     """Provides AuthService instance for dependency injection"""
#     return AuthService()


def get_leaderboard_deps() -> LeaderboardService:
    """Provides LeaderboardService instance for dependency injection"""
    return LeaderboardService()


def get_encryption_deps() -> EncryptionService:
    """?"""
    return EncryptionService()


@app.post(
    "/api-keys/generate",
    tags=[ApiTag.UTIL],
    description="Generate an API key from your Nakama server configuration.",
    name="Generate API Key",
)
async def generate_api_key(
    # TODO: Add validation on host input.
    host: str = Query(..., example="127.0.0.1", description="Your Nakama server host"),
    # TODO: Add validation on port input.
    port: str = Query(..., example="7350", description="Your Nakama server port"),
    ssl: SSLOption = Query(..., example="0", description="SSL enabled (0 or 1)"),
    # TODO: Add validation on server_key input.
    server_key: str = Query(
        ..., example="defaultkey", description="Your Nakama server key"
    ),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
):
    server_config = f"{host}:{port}:{ssl.value}:{server_key}"
    return {
        "api_key": encryption_service.encrypt_server_string(server_config),
        "server_config": server_config,
    }


# Account endpoints
@app.get(
    "/account",
    tags=[ApiTag.ACCOUNT],
    response_model=Account,
    summary="Fetch the current user's account.",
)
async def get_account(
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    session_token: str = Query(..., description=ApiDescriptions.SESSION_TOKEN),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    account_service: AccountService = Depends(get_account_deps),
) -> Account:
    server_string = encryption_service.decrypt_server_string(api_key)
    return await account_service.get(server_string, session_token)


@app.delete(
    "/account",
    tags=[ApiTag.ACCOUNT],
    response_model=DeleteAccountResponse,
    summary="Delete the current user's account.",
)
async def delete_account(
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    session_token: str = Query(..., description=ApiDescriptions.SESSION_TOKEN),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    account_service: AccountService = Depends(get_account_deps),
) -> DeleteAccountResponse:
    server_string = encryption_service.decrypt_server_string(api_key)
    return await account_service.delete(server_string, session_token)


@app.put(
    "/account",
    tags=[ApiTag.ACCOUNT],
    response_model=UpdateAccountResponse,
    summary="Update fields in the current user's account.",
)
async def update_account(
    update_data: UpdateAccountRequest,
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    session_token: str = Query(..., description=ApiDescriptions.SESSION_TOKEN),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    account_service: AccountService = Depends(get_account_deps),
) -> UpdateAccountResponse:
    server_string = encryption_service.decrypt_server_string(api_key)
    return await account_service.update(server_string, session_token, update_data)


@app.post(
    "/authenticate/email",
    tags=[ApiTag.ACCOUNT],
    response_model=Session,
    summary="Authenticate a user with an email+password against the server.",
)
async def authenticate_email(
    request: AccountEmail,
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    account_service: AccountService = Depends(get_account_deps),
) -> Session:
    server_string = encryption_service.decrypt_server_string(api_key)
    return await account_service.authenticate_email(server_string, request)


# # Authentication endpoints
# @app.post(
#     "/login-email",
#     tags=[ApiTag.AUTHENTICATION],
#     description="Authenticates a user's email credentials against the server.",
#     response_model=Session,
#     name="Login Email",
# )
# async def login_email(
#     request: EmailAuthRequest,  # Email authentication request data
#     api_key: str = Query(..., description=ApiDescriptions.API_KEY),
#     encryption_service: EncryptionService = Depends(get_encryption_deps),
#     auth: AuthService = Depends(get_auth_deps),
# ):
#     """Authenticates a user's email credentials against the server."""
#     server_string = encryption_service.decrypt_server_string(api_key)
#     return await auth.login_email(server_string, request)


# @app.post(
#     "/signup-email",
#     tags=[ApiTag.AUTHENTICATION],
#     description="Create a new user via email credentials against the server.",
#     response_model=AuthenticateEmailResponse,
#     name="Signup Email",
# )
# async def signup_email(
#     request: EmailCreateRequest,  # Email authentication request data
#     api_key: str = Query(..., description=ApiDescriptions.API_KEY),
#     encryption_service: EncryptionService = Depends(get_encryption_deps),
#     auth: AuthService = Depends(get_auth_deps),
# ):
#     """Create a new user via email credentials against the server."""
#     server_string = encryption_service.decrypt_server_string(api_key)
#     return await auth.signup_email(server_string, request)


# General endpoints
@app.get("/", response_class=HTMLResponse, tags=[ApiTag.GENERAL])
async def default(request: Request):
    """Serves the main application landing page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,  # Required by Jinja2
            "title": _title,
            "description": ApiDescriptions.APP,
        },
    )


# Leaderboard endpoints
@app.get(
    "/leaderboard",
    tags=[ApiTag.LEADERBOARD],
    description="Retrieves leaderboard records.",
    response_model=LeaderboardResponse,
    name="Get Leaderboard Records",
)
async def getLeaderboardRecords(
    limit: int,
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    session_token: str = Query(..., description=ApiDescriptions.SESSION_TOKEN),
    leaderboard_id: str = Query(..., example="weekly_leaderboard"),
    next_cursor: Optional[str] = Query(default=None),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    leaderboard: LeaderboardService = Depends(get_leaderboard_deps),
):
    """Retrieves leaderboard records"""
    server_string = encryption_service.decrypt_server_string(api_key)
    return await leaderboard.get_records(
        server_string,
        session_token,
        leaderboard_id,
        limit,
        next_cursor,
    )


@app.post(
    "/createLeaderboardRecord",
    tags=[ApiTag.LEADERBOARD],
    description="Creates a leaderboard record.",
    response_model=LeaderboardRecordResponse,
    name="Create Leaderboard Record",
)
async def createLeaderboardRecord(
    request: LeaderboardCreateRequest,
    api_key: str = Query(..., description=ApiDescriptions.API_KEY),
    session_token: str = Query(..., description=ApiDescriptions.SESSION_TOKEN),
    leaderboard_id: str = Query(..., example="weekly_leaderboard"),
    encryption_service: EncryptionService = Depends(get_encryption_deps),
    leaderboard: LeaderboardService = Depends(get_leaderboard_deps),
):
    """Retrieves leaderboard records"""
    server_string = encryption_service.decrypt_server_string(api_key)
    return await leaderboard.create_record(
        server_string,
        session_token,
        leaderboard_id,
        request,
    )
