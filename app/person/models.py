from core.database import Base
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy_file import ImageField
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

class PersonModel(Base):
    __tablename__ = "person"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    family_name = Column(String(512))
    creation_date = Column(DateTime, nullable=False, default=func.now())
    is_admin = Column(Boolean, nullable=False, default=False,server_default='False')
    is_rabbie = Column(Boolean, nullable=False, default=False,server_default='False')
    image = Column(
        ImageField(upload_storage="person_storage"),
        nullable=True
    )
    users = relationship("UserModel",back_populates="person")
    # asked_questions = relationship(
    #     "QAModel",
    #     foreign_keys="QAModel.talmid_id",
    #     back_populates="talmid"
    # )
    #
    # answered_questions = relationship(
    #     "QAModel",
    #     foreign_keys="QAModel.rabbie_id",
    #     back_populates="rabbie"
    # )

    def __str__(self):
        return f"{self.name} - {self.family_name}"