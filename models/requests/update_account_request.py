from typing import Optional
from pydantic import BaseModel


class UpdateAccountRequest(BaseModel):
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    lang_tag: str | None = None
