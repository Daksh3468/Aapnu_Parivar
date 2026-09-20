import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.db import Base


class Address(Base):
    __tablename__ = "address"

    address_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    line1 = Column(String(255), nullable=False)
    village_or_town = Column(String(100), nullable=False)
    taluka = Column(String(100), nullable=False)
    district_code = Column(Integer, ForeignKey("district.district_code"), nullable=False, index=True)
    pincode = Column(String(6), ForeignKey("pincode_master.pincode"), nullable=False, index=True)

    district = relationship("District", back_populates="addresses")
    families = relationship("Family", back_populates="address")
