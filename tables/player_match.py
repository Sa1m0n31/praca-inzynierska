from sqlalchemy import Column, Integer, Float
from .base import Base


class PlayerMatch(Base):
    __tablename__ = 'player_match'

    player_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, primary_key=True)
    position = Column(Integer)
    minutes_played = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    penalties = Column(Integer)
    penalties_made = Column(Integer)
    passes = Column(Integer)
    completed_passes = Column(Integer)
    progressive_passes = Column(Integer)
    xG = Column(Float)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    touches = Column(Integer)
    dribbles = Column(Integer)
    dribbles_completed = Column(Integer)
