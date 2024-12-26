from typing import Any
from fastapi import HTTPException
import requests
from email_validator import validate_email, EmailNotValidError
from models.requests.email_auth_request import EmailAuthRequest
from models.requests.email_create_request import EmailCreateRequest
from models.responses.authenticate_email_response import AuthenticateEmailResponse
 
from utils.server_string_util import buildClientConfig, encode_auth, get_base_url

# https://heroiclabs.com/docs/nakama/concepts/authentication/

class BaseAuthService:
   def __init__(self):
       self.headers = {
           "X-Requested-With": "XMLHttpRequest", 
           "Content-Type": "application/json"
       }

   async def _setup_auth(self, server_string: str, email: str) -> tuple[str, str]:
       client = buildClientConfig(server_string)
       auth = encode_auth(f"{client.serverKey}:")
       validate_email(email)
       # TODO: Validate password, minimum 8 characters.
       base_url = get_base_url(client.host, client.ssl, client.httpPort)
       endpoint = f"{base_url}account/authenticate/email"
       return auth, endpoint

class AuthService(BaseAuthService):
    def __init__(self):
        super().__init__()
    # Note: "By default the system will create a user automatically 
    # if the identifier used to authenticate did not previously 
    # exist in the system." 
    
    # This means if the email is not in the database, it will
    # creat a new account with that email, even with create 
    # set to FALSE.
    async def login_email(
        self,
        server_string: str,
        request: EmailAuthRequest,
    ) -> AuthenticateEmailResponse:
        try:
            auth, endpoint = await self._setup_auth(server_string, request.email)
            headers = {**self.headers, "Authorization": f"Basic {auth}"}
            data = {
                "email": request.email,
                "password": request.password,
                "create": False,
            }
            response: Any = requests.post(f"{endpoint}", headers=headers, json=data)
            response.raise_for_status()
            res = response.json()

            return AuthenticateEmailResponse(
                token=res["token"], refresh_token=res["refresh_token"]
            )
        except EmailNotValidError:
            raise HTTPException(status_code=422, detail="Invalid email address format")
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to authenticate: {str(e)}"
            )
            
    # Note: For some reason, no exception arises if the user's credentials
    # are already in the system. They just get logged in... :/
    async def signup_email(
        self,
        server_string: str,
        request: EmailCreateRequest,
    ) -> AuthenticateEmailResponse:
        try:
            auth, endpoint = await self._setup_auth(server_string, request.email)
            headers = {**self.headers, "Authorization": f"Basic {auth}"}
            data: dict[str, Any] = {
                "email": request.email,
                "password": request.password,
                "create": True,
            }
            response: Any = requests.post(f"{endpoint}?username={request.username}", headers=headers, json=data)
            response.raise_for_status()
            res = response.json()
        
            return AuthenticateEmailResponse(
                token=res["token"], refresh_token=res["refresh_token"]
            )
        except EmailNotValidError:
            raise HTTPException(status_code=422, detail="Invalid email address format")
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to authenticate: {str(e)}"
            )