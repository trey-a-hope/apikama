from pydantic import BaseModel


class DeleteAccountResponse(BaseModel):
    message: str = "Account successfully deleted"
