from pydantic import BaseModel
from models.user import User


class Account(BaseModel):
    user: User
    email: str
    wallet: str
