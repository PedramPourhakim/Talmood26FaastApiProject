from core.database import Base
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.sql import func
import uuid

class PersonModel(Base):
    __tablename__ = "person"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    phone = Column(String(11), nullable=False)
    creation_date = Column(DateTime, nullable=False, default=func.now())
    verification_code = Column(Integer, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    def __str__(self):
        return f"{self.email} - {self.phone}"