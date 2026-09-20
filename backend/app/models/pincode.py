from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class PincodeMaster(Base):
    __tablename__ = "pincode_master"

    pincode = Column(String(6), primary_key=True, index=True)
    district_code = Column(Integer, ForeignKey("district.district_code"), nullable=False, index=True)
    taluka = Column(String(100), nullable=False)
    area_name = Column(String(150), nullable=False)

    district = relationship("District", back_populates="pincodes")
