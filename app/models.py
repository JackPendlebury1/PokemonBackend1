from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(String)
    userImage = Column(LargeBinary)

    favourites = relationship("Favourites", back_populates="owner")

class Favourites(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True, )
    favourite_index = Column(Integer)
    owner_id = Column(String, ForeignKey("users.id"))

    owner = relationship("User", back_populates="favourites")