from sqlalchemy import Column, String, DateTime
from setup_db import Base


class KeyValue(Base):
    key = Column(String(255), primary_key=True)
    value = Column(String(255), primary_key=True)
    expiration_time = Column(DateTime)

