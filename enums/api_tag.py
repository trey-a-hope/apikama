# API endpoint tags for documentation organization
from enum import Enum


class ApiTag(Enum):
    ACCOUNT = "Account"
    AUTHENTICATION = "Authentication"
    LEADERBOARD = "Leaderboard"
    GENERAL = "General"
    UTIL = "Util"
