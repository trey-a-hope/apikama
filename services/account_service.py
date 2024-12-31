from typing import Dict
from fastapi import HTTPException, status
import requests
from models.account import Account
from models.client_config import ClientConfig
from models.requests.update_account_request import UpdateAccountRequest
from models.responses.delete_account_response import DeleteAccountResponse
from models.responses.update_account_response import UpdateAccountResponse
from models.user import User
from utils.server_string_util import buildClientConfig, get_base_url


class AccountService:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def _get_base_config(
        self, server_string: str, session_token: str
    ) -> tuple[str, Dict[str, str]]:
        """Set up common configuration for API calls"""
        client: ClientConfig = buildClientConfig(server_string=server_string)
        base_url: str = get_base_url(
            host=client.host, ssl=client.ssl, http_port=client.httpPort
        )

        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {session_token}"

        return base_url, headers

    def _build_endpoint(self, base_url: str) -> str:
        """Construct the endpoint URL"""
        return f"{base_url}account"

    def _handle_response_errors(
        self, response: requests.Response, operation: str
    ) -> None:
        """Common error handling for API responses"""
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not exist or unauthorized.",
            )
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to {operation} account: {str(e)}.",
            )

    def _parse_user_data(self, data: Dict) -> User:
        """Parse user data from API response"""
        user_data = data.get("user", {})
        print(user_data)
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
