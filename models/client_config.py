from pydantic import BaseModel


class ClientConfig(BaseModel):
    host: str
    ssl: bool
    serverKey: str  # TODO: snake_case
    httpPort: int  # TODO: snake_case
