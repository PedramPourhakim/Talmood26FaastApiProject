from core.database import Base
from sqlalchemy import Column,String
from sqlalchemy.orm import relationship
import uuid

class PaymentTypeModel(Base):
    __tablename__ = 'payment_type'
    id =  Column(String(36), primary_key=True ,default=lambda : str(uuid.uuid4()))
    title = Column(String(255), nullable=False,unique=True)
    payment_accounts = relationship("PaymentAccountModel", back_populates="payment_type")

    def __str__(self):
        return self.title