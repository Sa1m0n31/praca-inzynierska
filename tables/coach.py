from sqlalchemy import Column, Integer, String
from .base import Base


class Coach(Base):
    __tablename__ = 'coach'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
