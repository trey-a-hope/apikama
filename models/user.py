from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    displayName: str | None = None
    avatarUrl: str | None = None
    langTag: str | None = None
    online: bool | None = None


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI2Y2I5MDM2OS04ODIwLTQ4ZGMtOGRkMS1lY2Y0MjRkOTA2N2UiLCJ1c24iOiJLaW5nQ29sZSIsImV4cCI6MTczNTcwNTExOX0.PWoxFOuyUv-oVWrk6iEhDThKLlxHP577Hp_yuldOCJg
