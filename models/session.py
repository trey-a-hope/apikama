from pydantic import BaseModel


class Session(BaseModel):
    created: bool | None = None
    token: str
    refresh_token: str
