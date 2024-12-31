from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    displayName: str | None = None
    avatarUrl: str | None = None
    langTag: str | None = None
    online: bool | None = None
