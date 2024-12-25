from typing import Any
from fastapi import FastAPI, HTTPException, Path
import requests
import base64
from email_validator import validate_email, EmailNotValidError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models.responses.authenticate_email_response import AuthenticateEmailResponse
from models.client_config import ClientConfig
from models.email_auth_request import EmailAuthRequest
from enum import Enum
from urllib.parse import unquote
from models.responses.get_account_response import GetAccountResponse

# uvicorn main:app --reload

server_string = "24.144.85.68:7350:0:defaultkey"

_title: str = "Pykama API"
_description: str = (
    f"A free API for the Nakama game server, built in Python. My server string: {server_string}"
)
_server_string_description: str = (
    f"String parsed to generate client config - {server_string}"
)

app: FastAPI = FastAPI(
    title=_title,
    description=_description,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# TODO: Make session tokens last longer, they expire to quickly right now.
# TODO: This causes the two params to be seperated and throws off json parsing.
#  = Path(title='Client Config', description='Configuration model for connecting to a Nakama server instance.')
#  = Path(title='Email Auth Request', description='Request model for email-based authentication in Nakama.')

class ApiTag(Enum):
    ACOUNT = "Acount"
    AUTHENTICATION = "Authentication"
    GENERAL = "General"


@app.get(
    "/getAccount",
    tags=[ApiTag.ACOUNT],
    description="Retrieves the user's account information.",
    response_model=GetAccountResponse,
    name="Get Account",
)
async def getAccount(
    server_string: str,
    session_token: str,
):
    try:
        decoded_string: str = unquote(server_string)

        client: ClientConfig = _decode_server_string(decoded_string)

        baseUrl: str = _get_base_url(
            host=client.host, ssl=client.ssl, http_port=client.httpPort
        )
        print(f"Base URL: {baseUrl}")

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session_token}",
        }
        print(f"Headers: {headers}")

        endpoint: str = f"{baseUrl}account"
        print(f"Endpoint: {endpoint}")

        response: Any = requests.get(endpoint, headers=headers)

        response.raise_for_status()

        data = response.json()

        print(data)

        return GetAccountResponse(
            id=data["user"]["id"],
            email=data["email"],
            username=data["user"]["username"],
            create_time=data["user"]["create_time"],
            update_time=data["user"]["update_time"],
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account: {str(e)}")


@app.post(
    "/authenticateEmail",
    tags=[ApiTag.AUTHENTICATION],
    description="Authenticates a user's email credentials against the server.",
    response_model=AuthenticateEmailResponse,
    name="Authenticate Email",
)
async def authenticateEmail(
    server_string: str,
    request: EmailAuthRequest,
):
    try:
        decoded_string: str = unquote(server_string)

        client: ClientConfig = _decode_server_string(decoded_string)

        auth: str = _encode_auth(f"{client.serverKey}:")
        print(f"Auth: {auth}")

        base_url: str = _get_base_url(
            host=client.host, ssl=client.ssl, http_port=client.httpPort
        )
        print(f"Base URL: {base_url}")

        validate_email(request.email)
        print(f"Email {request.email} is valid.")

        headers: dict[str, str] = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        }
        print(f"Headers: {headers}")

        data: dict[str, Any] = {
            "email": request.email,
            "password": request.password,
            "create": request.create,
        }
        print(f"Data: {data}")

        endpoint: str = (
            f"{base_url}account/authenticate/email?username={request.username}"
        )
        print(f"Endpoint: {endpoint}")

        response: Any = requests.post(f"{endpoint}", headers=headers, json=data)

        response.raise_for_status()

        data: dict[str, Any] = response.json()

        return AuthenticateEmailResponse(
            token=data["token"], refresh_token=data["refresh_token"]
        )
    except EmailNotValidError:
        raise HTTPException(status_code=422, detail="Invalid email address format")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate: {str(e)}")


@app.get("/", response_class=HTMLResponse, tags=[ApiTag.GENERAL])
async def default():
    html_content = f"""
    <html>
        <head>
            <title>{_title}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1, h2 {{ color: #2d3748; }}
                .section {{
                    background: #f7fafc;
                    padding: 1rem;
                    border-radius: 4px;
                    margin: 1rem 0;
                }}
                .endpoint {{
                    background: #edf2f7;
                    padding: 0.5rem;
                    border-radius: 4px;
                    margin: 0.5rem 0;
                }}
                .method {{
                    display: inline-block;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    background: #4299e1;
                    color: white;
                    font-size: 0.875rem;
                }}
                .method.get {{
                    background: #10B981;  /* Green for GET */
                }}
                .method.post {{
                    background: #3B82F6;  /* Blue for POST */
                }}
                .links a {{
                    color: #4299e1;
                    text-decoration: none;
                }}
                .links a:hover {{
                    text-decoration: underline;
                }}
                .todo-item {{
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem;
                    background: #edf2f7;
                    border-radius: 4px;
                    margin: 0.5rem 0;
                }}
                .todo-item::before {{
                    content: "⭕";
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 {_title}</h1>
                <p>{_description}</p>
                <p>Handles CORS issues to enable web browser compatibility.</p>
                <div class="section">
                    <h2>Documentation:</h2>
                    <ul>
                        <li><a href="/docs">Interactive API Documentation (Swagger UI)</a></li>
                        <li><a href="/redoc">Alternative Documentation (ReDoc)</a></li>
                    </ul>
                </div>

                <div class="section">
                    <h2>In Progress:</h2>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/getLeaderboardRecords</code>
                        <p>Returns a list of leaderboard records for the week.</p>
                    </div>
                </div>

                <div class="section">
                    <h2>ToDo:</h2>
                    <div class="todo-item">
                        Make session tokens last longer, they expire to quickly right now.
                    </div>
                    <div class="todo-item">
                        Apply PATH variables to params.
                    </div>
                </div>

                <div class="section">
                    <h2>Links & Resources:</h2>
                    <div class="links">
                        <p>📂 <a href="https://github.com/trey-a-hope/gift-grab" target="_blank">GitHub Repository</a></p>
                        <p>📚 <a href="https://heroiclabs.com/docs/nakama/" target="_blank">Nakama Documentation</a></p>
                    </div>
                </div>

                <div class="section">
                    <h2>Contact:</h2>
                    <p>Developer: Trey Hope</p>
                    <p>Email: <a href="mailto:trey.a.hope@gmail.com">trey.a.hope@gmail.com</a></p>
                </div>

                <div class="section">
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Status:</strong> Online</p>
                    <p><strong>Last Updated:</strong> December 2024</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content


# Convert auth string to base64 encoded string.
def _encode_auth(auth_string: str) -> str:
    auth_bytes: bytes = auth_string.encode("utf-8")
    return base64.b64encode(auth_bytes).decode("utf-8")


# Generate base URL string for Nakama server.
def _get_base_url(host: str, ssl: bool, http_port: int) -> str:
    protocol: str = "https" if ssl else "http"
    return f"{protocol}://{host}:{http_port}/v2/"


def _encode_server_string(config: ClientConfig) -> str:
    # Format: host:port:ssl:key
    # Example: "24.144.85.68:7350:0:defaultkey"
    return (
        f"{config.host}:{config.httpPort}:{1 if config.ssl else 0}:{config.serverKey}"
    )


def _decode_server_string(server_str: str) -> ClientConfig:
    host, port, ssl, key = server_str.split(":")
    return ClientConfig(
        host=host,
        ssl=ssl == "1",
        serverKey=key,  # TODO: Make this more secretive...
        httpPort=int(port),
    )
