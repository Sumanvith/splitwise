from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from app.database import Base


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    group_id = Column(
        Integer, ForeignKey('groups.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    paid_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(String, nullable=False)
    total_amount = Column(Integer, nullable=False)
    split_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class ExpenseShare(Base):
    __tablename__ = 'expense_shares'

    expense_id = Column(
        Integer, ForeignKey('expenses.id', ondelete='CASCADE'), primary_key=True
    )
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    share_amount = Column(Integer, nullable=False)
