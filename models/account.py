from pydantic import BaseModel


class Account(BaseModel):
    id: str
    username: str
    email: str
