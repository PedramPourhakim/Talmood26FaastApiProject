import datetime
from core.database import Base
from sqlalchemy import Column,String,DateTime
from sqlalchemy.sql import func
import uuid

class ParashaModel(Base):
    __tablename__ = 'parasha'

    id = Column(String(36), primary_key=True, default=lambda : str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(String(), nullable=False)
    image_path = Column(String(255), nullable=False)
    creation_date = Column(DateTime, nullable=False, default=func.now())
    image_file = None

    def __str__(self):
        return f"{self.title} - {self.description} - {self.image_path}"
