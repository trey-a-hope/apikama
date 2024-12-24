from pydantic import BaseModel

class ClientConfig(BaseModel):
    host: str
    ssl: bool
    serverKey: str
    grpcPort: int # TODO: May not be required...
    httpPort: int