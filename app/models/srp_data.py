from sqlalchemy import Column, String, Text, CHAR

from ..database import Base


class SRPData(Base):
    __tablename__ = "srp_data"
    user_id = Column(CHAR(36), primary_key=True, index=True)
    salt = Column(String(512))
    verifier = Column(String(32))
