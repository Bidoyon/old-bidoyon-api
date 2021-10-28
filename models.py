from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str


class NewUser(BaseModel):
    username: str
    password: str
    permission: str


class OldUser(BaseModel):
    username: str


class Token(BaseModel):
    token: str


class NewPressing(BaseModel):
    number: Optional[int] = None
    added_juice: Optional[int] = 0
    added_apples: Optional[int] = 0


class NewInvestment(BaseModel):
    username: str
    apples: Optional[int] = 0


class Investor(BaseModel):
    username: Optional[str] = ""
