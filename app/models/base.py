from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, func, Column
from sqlalchemy.sql.schema import Identity
from sqlalchemy.sql.sqltypes import Integer


class Base(DeclarativeBase):
    id = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
        index=True
    )
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
