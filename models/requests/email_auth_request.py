from pydantic import BaseModel


class AccountEmail(BaseModel):
    email: str
    password: str
    create: bool
    username: str | None = None
