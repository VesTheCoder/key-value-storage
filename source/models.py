from sqlalchemy import Column, String, DateTime
from setup_db import Base


class KeyValue(Base):
    __tablename__ = "key_values"

    key = Column(String(255), primary_key=True)
    value = Column(String(255), nullable=True)
    expiration_time = Column(DateTime, nullable=True)
