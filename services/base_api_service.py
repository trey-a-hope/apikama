from typing import Dict
from fastapi import HTTPException, status
import requests
from utils.server_string_util import buildClientConfig, get_base_url


class BaseAPIService:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def _get_base_config(
        self, server_string: str, session_token: str
    ) -> tuple[str, Dict[str, str]]:
        client = buildClientConfig(server_string=server_string)
        base_url = get_base_url(
            host=client.host, ssl=client.ssl, http_port=client.httpPort
        )
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {session_token}"
        return base_url, headers
    
    def _build_auth_headers(self, auth: str) -> Dict[str, str]:
       headers = self.headers.copy()
       headers["Authorization"] = f"Basic {auth}"
       return headers

    def _handle_response_errors(
        self, response: requests.Response, operation: str
    ) -> None:
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access."
            )
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Operation failed: {str(e)}.",
            )
