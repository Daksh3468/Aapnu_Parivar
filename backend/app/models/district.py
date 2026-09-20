from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.db import Base


class District(Base):
    __tablename__ = "district"

    district_code = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    pincodes = relationship("PincodeMaster", back_populates="district")
    addresses = relationship("Address", back_populates="district")
