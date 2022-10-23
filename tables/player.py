from sqlalchemy import Column, Date, Integer, String
from .base import Base


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    birthday = Column(Date)
    nationality = Column(String)
