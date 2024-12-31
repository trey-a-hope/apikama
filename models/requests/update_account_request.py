from typing import Optional
from pydantic import BaseModel


class UpdateAccountRequest(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    lang_tag: Optional[str] = None
