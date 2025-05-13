from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class KeyValue(DeclarativeBase):
    key = Column(String(255), primary_key=True)
    value = Column(String(255), primary_key=True)
    expiration_time = Column(DateTime)

