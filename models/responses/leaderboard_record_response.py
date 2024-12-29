from typing import List
from pydantic import BaseModel


class LeaderboardRecordResponse(BaseModel):
    leaderboard_id: str
    owner_id: str
    username: str
    score: int
    num_score: int
    create_time: str
    update_time: str
    expiry_time: str
    rank: str
    max_num_score: int
