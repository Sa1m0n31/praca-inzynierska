from sqlalchemy import Column, Integer, String
from .base import Base


class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)
    name = Column(String)
