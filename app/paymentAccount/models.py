from core.database import Base
from sqlalchemy import Column,String,DateTime,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid


class PaymentAccountModel(Base):
    __tablename__ = "payment_account"

    id = Column(String(36), primary_key=True, default= lambda : str(uuid.uuid4()))
    account_title = Column(String(512),nullable=False)
    sheba_number = Column(String(26),nullable=False)
    creation_date = Column(DateTime, nullable=False, default=func.now())
    payment_type_id = Column(String(36), ForeignKey('payment_type.id'),nullable=False)
    payment_type = relationship("PaymentTypeModel", back_populates="payment_accounts")
    person_id = Column(String(36), ForeignKey('person.id'),nullable=False)
    person = relationship("PersonModel", back_populates="payment_accounts")
    payments = relationship("PaymentModel", back_populates="payment_account")

    def __str__(self):
        return f"{self.account_title}"