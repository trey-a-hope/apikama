from pydantic import BaseModel


class UpdateAccountResponse(BaseModel):
    message: str = "Account successfully updated"
