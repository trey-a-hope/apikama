from typing import Dict
from fastapi import HTTPException
import requests
from models.account import Account
from models.requests.update_account_request import UpdateAccountRequest
from models.responses.delete_account_response import DeleteAccountResponse
from models.responses.update_account_response import UpdateAccountResponse
from models.user import User
from services.base_api_service import BaseAPIService
from utils.server_string_util import buildClientConfig
from fastapi import HTTPException
import requests
from email_validator import EmailNotValidError
from models.requests.email_auth_request import AccountEmail
from models.session import Session
from utils.server_string_util import buildClientConfig, encode_auth
from utils.validators import validate_password


class AccountService(BaseAPIService):
    def _build_endpoint(self, base_url: str) -> str:
        return f"{base_url}account"

    def _parse_user_data(self, data: Dict) -> User:
        user_data = data.get("user", {})
        return User(
            id=user_data.get("id"),
            username=user_data.get("username"),
            displayName=user_data.get("displayName"),
            avatarUrl=user_data.get("avatarUrl"),
            langTag=user_data.get("langTag"),
            online=user_data.get("online"),
        )

    async def get(self, server_string: str, session_token: str) -> Account:
        """Get user account details"""
        base_url, headers = self._get_base_config(server_string, session_token)
        endpoint = self._build_endpoint(base_url)

        response = requests.get(endpoint, headers=headers)
        self._handle_response_errors(response, "get")

        data = response.json()
        user = self._parse_user_data(data)

        return Account(user=user, email=data.get("email"), wallet=data.get("wallet"))

    async def delete(
        self, server_string: str, session_token: str
    ) -> DeleteAccountResponse:
        """Delete user account"""
        base_url, headers = self._get_base_config(server_string, session_token)
        endpoint = self._build_endpoint(base_url)
        response = requests.delete(
            endpoint,
            headers=headers,
        )
        self._handle_response_errors(response, "delete")
        return DeleteAccountResponse()

    async def update(
        self, server_string: str, session_token: str, update_data: UpdateAccountRequest
    ) -> UpdateAccountResponse:
        """Update user account details"""
        base_url, headers = self._get_base_config(server_string, session_token)
        endpoint = self._build_endpoint(base_url)

        response = requests.put(
            endpoint, headers=headers, json=update_data.model_dump(exclude_none=True)
        )
        self._handle_response_errors(response, "update")
        return UpdateAccountResponse()

    async def authenticate_email(
        self,
        server_string: str,
        request: AccountEmail,
    ) -> Session:
        if not validate_password(request.password):
            raise HTTPException(
                status_code=422,
                detail="Password must be at least 8 characters long",
            )

        try:
            base_url, _ = self._get_base_config(server_string, "")
            client = buildClientConfig(server_string)
            auth = encode_auth(f"{client.serverKey}:")
            headers = self._build_auth_headers(auth)
            data = {
                "email": request.email,
                "password": request.password,
                "create": request.create,
            }

            response = requests.post(
                f"{base_url}account/authenticate/email{f'?username={request.username}' if request.username else ''}",
                headers=headers,
                json=data,
            )
            self._handle_response_errors(response, "login")
            res = response.json()

            return Session(
                created=res.get("created", None),
                token=res["token"],
                refresh_token=res["refresh_token"],
            )

        except EmailNotValidError:
            raise HTTPException(
                status_code=422,
                detail="Invalid email address format",
            )
