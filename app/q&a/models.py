from core.database import Base
from sqlalchemy import Column,String,DateTime,Boolean,ForeignKey,Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid


class QAModel(Base):
    __tablename__ = 'qa_model'

    id = Column(String(36),primary_key=True,default=lambda : str(uuid.uuid4()))
    question = Column(Text)
    answer = Column(Text,nullable=True)
    status= Column(Boolean,server_default='False',default=False)
    creation_date = Column(DateTime, nullable=False, default=func.now())
    rabbie_id = Column(String(36),ForeignKey('person.id'))
    talmid_id = Column(String(36),ForeignKey('person.id'))
    rabbie = relationship(
        "PersonModel",
        foreign_keys="QAModel.rabbie_id",
        back_populates="answered_questions"
    )

    talmid = relationship(
        "PersonModel",
        foreign_keys="QAModel.talmid_id",
        back_populates="asked_questions"
    )

    def __str__(self):
        return self.question
