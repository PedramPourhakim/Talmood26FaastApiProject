from core.database import Base
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
import uuid


class UserModel(Base):
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    phone = Column(String(11), nullable=False)
    verification_code = Column(Integer, nullable=True)
    creation_date = Column(DateTime, nullable=False, default=func.now())
    person_id = Column(String(36), ForeignKey('person.id'))


