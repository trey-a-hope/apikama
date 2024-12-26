from typing import Any
from fastapi import HTTPException
import requests
from models.client_config import ClientConfig
from models.responses.get_account_response import GetAccountResponse
from utils.server_string_util import buildClientConfig, get_base_url


class AccountService:
    async def get_account(
        self, server_string: str, session_token: str
    ) -> GetAccountResponse:
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

            return GetAccountResponse(
                id=data["user"]["id"],
                email=data["email"],
                username=data["user"]["username"],
                create_time=data["user"]["create_time"],
                update_time=data["user"]["update_time"],
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get account: {str(e)}"
            )
