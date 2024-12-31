from typing import Any
from fastapi import HTTPException
import requests
from models.account import Account
from models.client_config import ClientConfig
from models.user import User
from utils.server_string_util import buildClientConfig, get_base_url


class AccountService:
    async def get_account(self, server_string: str, session_token: str) -> Account:
        try:
            client: ClientConfig = buildClientConfig(server_string=server_string)

            baseUrl: str = get_base_url(
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

            user = User(
                id=data.get("user", {}).get("id", None),
                username=data.get("user", {}).get("username", None),
                displayName=data.get("user", {}).get("displayName", None),
                avatarUrl=data.get("user", {}).get("avatarUrl", None),
                langTag=data.get("user", {}).get("langTag", None),
                online=data.get("user", {}).get("online", None),
            )

            return Account(
                user=user,
                email=data.get("email"),
                wallet=data.get("wallet"),
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get account: {str(e)}",
            )
