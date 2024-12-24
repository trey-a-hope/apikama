from pydantic import BaseModel

class EmailAuthRequest(BaseModel):
    email: str
    password: str
    username: str
    create: bool