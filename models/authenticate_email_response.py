from pydantic import BaseModel

class AuthenticateEmailResponse(BaseModel):
    token: str
    refreshToken: str