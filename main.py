from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import base64
import json
from email_validator import validate_email, EmailNotValidError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='Gift Grab API',
    description='Wrapper for the Nakama gaming server.',
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

auth_string = 'defaultkey:'  # This is your original string
auth_bytes = auth_string.encode('utf-8')  # Convert to bytes
base64_auth = base64.b64encode(auth_bytes).decode('utf-8')  # Encode and convert back to string
 
_proxy = 'https://radiant-fortress-74557-a19cc3a8e264.herokuapp.com/'
_baseUrl = 'http://24.144.85.68:7350/v2/'

class EmailAuthRequest(BaseModel):
    email: str
    password: str
    username: str
    create: bool

@app.post("/authenticateEmail")
async def authenticateEmail(request: EmailAuthRequest):
    try:
        validate_email(request.email)

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64_auth}',
        }

        data = {
            "email": request.email,
            "password": request.password,
            "create": request.create,
        }

        endpoint = f'{_baseUrl}account/authenticate/email?username={request.username}'
        response = await requests.post(f'{_proxy}{endpoint}', headers=headers, json=data)
        response.raise_for_status()
        data = response.json()
        return data
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

# @app.get("/player/{user_id}/stats")
# async def get_player_stats(user_id: str, token: str):
#     try:
#         # Create session from token
#         session = await nakama_client.session_restore(token)
        
#         # Get player stats from storage
#         result = await nakama_client.read_storage_objects(
#             session,
#             [{"collection": "game_data", "key": "player_stats", "user_id": user_id}]
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))