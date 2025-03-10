from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Union

from  model import Base
import uuid


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(String(36), ForeignKey("user.id"), nullable=False)
    players = Column(Integer, nullable=False)
    datetime = Column(DateTime, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now())

    def __init__(self, user:str, players:int, datetime: DateTime, created_at:Union[DateTime, None] = None):
                 
        """
        Cria um Schedule

        Arguments:
            user: id do usuário.
            players: quantidade de jogadores
            datetime: data e hora do jogo
            created_at: data de quando o jogo foi inserido à base
        """
        self.user = user
        self.players = players
        self.datetime = datetime

        if created_at:
            self.created_at = created_at