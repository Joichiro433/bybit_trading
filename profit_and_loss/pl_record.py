from datetime import datetime
from typing import Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, DateTime, String, Float

from profit_and_loss.base_db import Base, session_scope
from logger import Logger

logger = Logger()


class PL:
    def __init__(
            self,
            timestamp: datetime,
            equity: float,
            side: str) -> None:
        self.timestamp : datetime = timestamp
        self.equity : float = equity
        self.side : str = side


class ProfitAndLoss(Base):
    __tablename__ = 'profit_and_loss'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    equity = Column(Float, nullable=False)
    side = Column(String(255), nullable=False)

    # CRUD処理
    @classmethod
    def insert(cls, pl: PL) -> None:
        pl = cls(**pl.__dict__)
        try:
            with session_scope() as session:
                session.add(pl)
        except IntegrityError as e:
            logger.error(e)

    @classmethod
    def get(cls, time: datetime) -> Union[Base, None]:
        with session_scope() as session:
            row : Union[Base, None] = session.query(cls).filter(cls.timestamp==time).first()
            if row is None:
                return None
            return row

    def update(self) -> None:
        with session_scope() as session:
            session.add(self)

    @classmethod
    def delete(cls, time: datetime) -> None:
        with session_scope() as session:
            session.query(cls).filter(cls.timestamp==time).delete()