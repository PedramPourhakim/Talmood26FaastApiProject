from core.database import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger,Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SqlEnum
import uuid


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class PaymentModel(Base):
    __tablename__ = 'payment'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(BigInteger,nullable=False)
    description = Column(String(500))
    authority = Column(String(255))
    ref_id = Column(String(255))
    card_pan = Column(String(25))
    fee = Column(Integer())
    status = Column(
        SqlEnum(PaymentStatusEnum),
        nullable=False,
        default=PaymentStatusEnum.PENDING
    )
    payment_account_id = Column(String(36), ForeignKey('payment_account.id'), nullable=False)
    payment_account = relationship("PaymentAccountModel", back_populates="payments")
    creation_date = Column(DateTime, nullable=False, default=func.now())
    paid_at = Column(DateTime)
    person_id = Column(String(36), ForeignKey("person.id"),nullable=False)
    person = relationship("PersonModel",back_populates="payments")