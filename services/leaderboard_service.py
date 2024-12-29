from typing import Any, List
from fastapi import HTTPException
import requests
from models.client_config import ClientConfig
from models.requests.leaderboard_create_request import LeaderboardCreateRequest
from models.responses.leaderboard_record_response import (
    LeaderboardRecordResponse,
)
from models.responses.leaderboard_response import LeaderboardResponse
from utils.server_string_util import buildClientConfig, encode_auth, get_base_url


class BaseLeaderboardService:
    def __init__(self):
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }

    async def _setup_auth(self, server_string: str, leaderboard_id: str) -> str:
        client = buildClientConfig(server_string)
        base_url = get_base_url(client.host, client.ssl, client.httpPort)
        endpoint = f"{base_url}leaderboard/{leaderboard_id}"
        return endpoint


class LeaderboardService(BaseLeaderboardService):
    def __init__(self):
        super().__init__()

    async def create_record(
        self,
        server_string: str,
        session_token: str,
        leaderboard_id: str,
        request: LeaderboardCreateRequest,
    ) -> LeaderboardRecordResponse:
        try:
            endpoint = await self._setup_auth(server_string, leaderboard_id)
            headers = {**self.headers, "Authorization": f"Bearer {session_token}"}
            data = {
                "score": request.score,
            }
            response: Any = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()

            return LeaderboardRecordResponse(
                leaderboard_id=data["leaderboard_id"],
                owner_id=data["owner_id"],
                username=data["username"],
                score=data["score"],
                num_score=data["num_score"],
                create_time=data["create_time"],
                update_time=data["update_time"],
                expiry_time=data["expiry_time"],
                rank=data["rank"],
                max_num_score=data["max_num_score"],
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create record: {str(e)}"
            )

    async def get_records(
        self,
        server_string: str,
        session_token: str,
        leaderboard_id: str,
        limit: int,
        next_cursor: str | None = None,
    ) -> LeaderboardResponse:
        try:
            endpoint = await self._setup_auth(server_string, leaderboard_id)
            headers = {**self.headers, "Authorization": f"Bearer {session_token}"}

            # Apply required limit.
            endpoint += f"?limit={limit}"

            # Use optional cursor.
            if next_cursor is None:
                print("No cursor applied.")
            else:
                endpoint += f"&cursor={next_cursor}"

            response: Any = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()
            print("---")
            print(data)
            print("---")
            if not data:
                return LeaderboardResponse(
                    records=[],
                    next_cursor="",
                )

            next_cursor = ""
            if "next_cursor" in data:
                next_cursor = data["next_cursor"]

            return LeaderboardResponse(
                records=data["records"],
                next_cursor=next_cursor,
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get leaderboard records: {str(e)}"
            )
