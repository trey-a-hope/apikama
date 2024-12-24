from typing import Any
from fastapi import FastAPI, HTTPException, Path
import requests
import base64
from email_validator import validate_email, EmailNotValidError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models.authenticate_email_response import AuthenticateEmailResponse
from models.client_config import ClientConfig
from models.email_auth_request import EmailAuthRequest

# uvicorn main:app --reload

_title: str = 'Pykama API'
_description: str = 'A free, Python-based API for the Nakama game server.'

app: FastAPI = FastAPI(
    title=_title,
    description=_description,
    version="1.0.0",
    docs_url="/docs",   # Swagger UI endpoint
    redoc_url="/redoc"  # ReDoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# TODO: Test this in Flutter, may not need proxy :)
_proxy: str = 'https://radiant-fortress-74557-a19cc3a8e264.herokuapp.com/'
#    

# NOTE: There isn't a "dev" mode technically right now.
# Since I am not running the server locally.    
# {
#   "client": {
#     "host": "24.144.85.68",
#     "ssl": false,
#     "serverKey": "defaultkey",
#     "grpcPort": 7351,
#     "httpPort": 7350
#   },
#   "request": {
#     "email": "trey.a.hope@gmail.com",
#     "password": "Peachy4040",
#     "username": "trey.codes",
#     "create": true
#   }
# }

# TODO: This causes the two params to be seperated and throws off json parsing.
#  = Path(title='Client Config', description='Configuration model for connecting to a Nakama server instance.')
#  = Path(title='Email Auth Request', description='Request model for email-based authentication in Nakama.')

@app.get('/getAccount',
        tags=["Account"],
        description='Retrieves the user\'s account information.',
        # response_model=AuthenticateEmailResponse,
        name='Get Account')
async def getAccount(uid: str):
    return {'account': 'trey'}

@app.post("/authenticateEmail", 
          tags=["Authentication"], 
          description='Authenticates a user\'s email credentials against the server.',
          response_model=AuthenticateEmailResponse,
          name='Authenticate Email')
async def authenticateEmail(client: ClientConfig, request: EmailAuthRequest):
    try:
        auth: str = _encode_auth(f'{client.serverKey}:')
        print(f'Auth: {auth}')
                
        baseUrl: str = _get_base_url(host=client.host, ssl=client.ssl, http_port=client.httpPort)
        print(f'Base URL: {baseUrl}')
                
        validate_email(request.email)
        print(f'Email {request.email} is valid.')

        headers: dict[str, str] = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}',
        }
        print(f'Headers: {headers}')

        data: dict[str, Any] = {
            "email": request.email,
            "password": request.password,
            "create": request.create,
        }
        print(f'Data: {data}')

        endpoint: str = f'{_proxy}{baseUrl}account/authenticate/email?username={request.username}'
        print(f'Endpoint: {endpoint}')
        
        response: Any = requests.post(f'{endpoint}', headers=headers, json=data)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return AuthenticateEmailResponse(token=data['token'], refreshToken=data['refresh_token'])
    except EmailNotValidError:
        raise HTTPException(
            status_code=422,
            detail="Invalid email address format"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to authenticate: {str(e)}"
        )
    
@app.get("/", 
         response_class=HTMLResponse,
         tags=["General"])
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
                    <h2>Available Endpoints:</h2>
                    <div class="endpoint">
                        <span class="method">POST</span>
                        <code>/authenticateEmail</code>
                        <p>Authenticate users with email and password</p>
                    </div>
                </div>

                <div class="section">
                    <h2>ToDo:</h2>
                    <div class="todo-item">
                        Endpoint - <strong>listLeaderboardRecords</strong>
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
   auth_bytes: bytes = auth_string.encode('utf-8')
   return base64.b64encode(auth_bytes).decode('utf-8')

# Generate base URL string for Nakama server.
def _get_base_url(host: str, ssl: bool, http_port: int) -> str:
   protocol: str = 'https' if ssl else 'http'
   return f'{protocol}://{host}:{http_port}/v2/'