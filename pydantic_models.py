from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    login: str


class UserModelResponse(UserModel):
    id: int


class MessageModel(BaseModel):
    send_mail: str
    login: str


class MessageResponse(BaseModel):
    id: int
    send_mail: str
    answer_mail: Optional[str] = None
    user_id: int