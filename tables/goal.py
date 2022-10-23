from .base import Base
from sqlalchemy import Column, Integer


class Goal(Base):
    __tablename__ = 'goal'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    scorer = Column(Integer)
    minute = Column(Integer)
    distance = Column(Integer)
