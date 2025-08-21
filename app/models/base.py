# models/base.py
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy import DateTime, func, Column


class Base(DeclarativeBase):
    pass


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
