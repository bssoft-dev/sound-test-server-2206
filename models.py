from builtins import bool
from pydantic import BaseModel
from fastapi_users import models
from typing import Optional
import pydantic
from pydantic import EmailStr
from bson import ObjectId

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str


class User(models.BaseUser):
    # customerCode: str
    # customerName: str
    name: Optional[str]
    createTime: Optional[str]
    phone: Optional[str]
    email: Optional[str]


class UserCreate(models.BaseUserCreate):
    # customerCode: Optional[str]
    # customerName: str
    name: Optional[str]
    createTime: Optional[str]
    phone: Optional[str]
    email: Optional[
        str
    ]  # don't modify this field, login error will be raised if it is changed


class UserUpdate(models.BaseUserUpdate):
    name: Optional[str]
    # username: Optional[str]
    phone: Optional[str]
    # password : Optional[str]
    email: Optional[EmailStr]


class UserSuperUpdate(BaseModel):
    is_superuser: bool = False


class UserDB(User, models.BaseUserDB):
    # customerCode: str
    # customerName: str
    name: Optional[str]
    createTime: Optional[str]
    phone: Optional[str]
