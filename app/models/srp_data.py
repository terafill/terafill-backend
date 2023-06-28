from sqlalchemy import Column, String, Text

from ..database import Base


class SRPData(Base):
    __tablename__ = "srp_data"
    user_id = Column(String(128), primary_key=True, index=True)
    salt = Column(Text)
    verifier = Column(Text)
