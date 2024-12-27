from typing import List
from pydantic import BaseModel

from models.responses.leaderboard_record_response import LeaderboardRecordResponse


class LeaderboardResponse(BaseModel):
    records: List[LeaderboardRecordResponse]
