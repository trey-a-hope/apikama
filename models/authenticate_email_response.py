from pydantic import BaseModel

class AuthenticateEmailResponse(BaseModel):
    token: str
    refresh_token: str