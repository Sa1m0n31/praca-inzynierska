from .base import Base
from sqlalchemy import Column, Integer, String


class League(Base):
    __tablename__ = 'league'

    id = Column(Integer, primary_key=True)
    name = Column(String)