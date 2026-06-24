from core.database import Base
from sqlalchemy import Column, String, DateTime,Text
from sqlalchemy.sql import func
from sqlalchemy_file import ImageField
import uuid


class ParashaModel(Base):
    __tablename__ = 'parasha'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    creation_date = Column(DateTime, nullable=False, default=func.now())

    # ImageField با sqlalchemy-file
    image = Column(
        ImageField(upload_storage="parasha_storage"),
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "image_url": self.image_url,
        }

    def __str__(self):
        return f"{self.title}"

    @property
    def image_url(self):
        if self.image and self.image.path:
            return f"/static/parasha_images/{self.image.path.split('/')[-1]}"
        return None