from typing import Any
from fastapi import HTTPException
import requests
from email_validator import validate_email, EmailNotValidError
from models.responses.authenticate_email_response import AuthenticateEmailResponse
from models.client_config import ClientConfig
from models.email_auth_request import EmailAuthRequest
from utils.server_string_util import buildClientConfig, encode_auth, get_base_url


class AuthService:
    async def authenticate_email(
        self,
        server_string: str,
        request: EmailAuthRequest,
    ) -> AuthenticateEmailResponse:
        try:
            client: ClientConfig = buildClientConfig(server_string=server_string)

            auth: str = encode_auth(f"{client.serverKey}:")
            print(f"Auth: {auth}")

            base_url: str = get_base_url(
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
            raise HTTPException(
                status_code=500, detail=f"Failed to authenticate: {str(e)}"
            )
