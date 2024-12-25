from pydantic import BaseModel


class GetAccountResponse(BaseModel):
    id: str
    email: str
    username: str
    create_time: str
    update_time: str
