from sqlalchemy import Column, Integer, String
from .base import Base


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    season = Column(String)
    league = Column(Integer)
