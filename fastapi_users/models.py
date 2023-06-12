import uuid
from typing import List, Optional, TypeVar

from pydantic import UUID4, BaseModel, EmailStr, Field


class CreateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})
    
class UpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUser(CreateDictModel):
    """Base User model."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    # email: Optional[EmailStr] = None
    username: str
    email: Optional[str] = ''
    is_active: bool = True
    is_superuser: bool = True
    is_hyperuser: bool = False
    is_verified: bool = False
    # createTime: str

class BaseUserCreate(CreateDictModel):
    username: str
    # email: Optional[EmailStr]
    email: Optional[str] = ''
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = True
    is_hyperuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    # createTime: str

class UserCreateResponse(BaseUser):
    username: str
    email: Optional[str] = ''
    name: str
    # createTime: str

class BaseUserUpdate(UpdateDictModel):
    password: Optional[str]
    # email: Optional[EmailStr]
    email: Optional[str]
    # is_active: Optional[bool]
    # is_superuser: Optional[bool]
    # is_hyperuser: Optional[bool]
    # is_verified: Optional[bool]    

class BaseUserDB(BaseUser):
    hashed_password: str
    
    class Config:
        orm_mode = True


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)
UD = TypeVar("UD", bound=BaseUserDB)


class BaseOAuthAccount(BaseModel):
    """Base OAuth account model."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str
    # account_userId: str

    class Config:
        orm_mode = True


class BaseOAuthAccountMixin(BaseModel):
    """Adds OAuth accounts list to a User model."""

    oauth_accounts: List[BaseOAuthAccount] = []
