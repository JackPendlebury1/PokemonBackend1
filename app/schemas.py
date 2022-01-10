from typing import List, Optional

from pydantic import BaseModel

class UserBase(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name   : Optional[str] = None
    email: Optional[str] = None

class FavouritesBase(BaseModel):
    favourite_index: Optional[int] = None


class Favourites(FavouritesBase):
    owner_id: str
    
    class Config:
        orm_mode = True

class FavouritesCreate(FavouritesBase):
    pass

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserUpdateImage(UserBase):
    userImage: Optional[str] = None

class User(UserBase):
    id: Optional[str] = None
    created_at  : Optional[str] = None
    hashed_password: Optional[str] = None
    userImage : Optional[bytes] = None
    favourites: List[Favourites] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None