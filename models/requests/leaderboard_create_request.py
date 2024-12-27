from pydantic import BaseModel


class LeaderboardCreateRequest(BaseModel):
    score: int