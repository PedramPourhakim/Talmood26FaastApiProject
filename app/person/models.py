from core.database import Base
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

class PersonModel(Base):
    __tablename__ = "person"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    family_name = Column(String(512))
    creation_date = Column(DateTime, nullable=False, default=func.now())
    is_admin = Column(Boolean, nullable=False, default=False)
    is_rabbie = Column(Boolean, nullable=False, default=False)
    image_path = Column(String(255), nullable=True)
    image_file = None
    users = relationship("UserModel", backref="person")

    def __str__(self):
        return f"{self.name} - {self.family_name}"