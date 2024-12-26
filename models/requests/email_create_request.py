from pydantic import BaseModel


class EmailCreateRequest(BaseModel):
    email: str
    password: str
    username: str