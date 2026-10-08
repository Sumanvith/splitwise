from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from app.database import Base


class Settlement(Base):
    __tablename__ = 'settlements'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    from_user = Column(Integer, ForeignKey('users.id'), nullable=False)
    to_user = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
