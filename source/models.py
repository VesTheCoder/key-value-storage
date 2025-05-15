from sqlalchemy import Column, String, DateTime
from typing import Optional
from datetime import datetime

from setup_db import Base


class KeyValue(Base):
    """
    Represents a key-value model stored in the database.
    """
    __tablename__ = "key_values"

    key: str = Column(String(255), primary_key=True)
    value: Optional[str] = Column(String(255), nullable=True)
    expiration_time: Optional[datetime] = Column(DateTime, nullable=True)
