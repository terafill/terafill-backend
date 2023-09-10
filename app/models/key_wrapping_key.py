from sqlalchemy import Column, String, Text, CHAR

from ..database import Base


class KeyWrappingKey(Base):
    __tablename__ = "key_wrapping_keys"
    user_id = Column(CHAR(36), primary_key=True, index=True)
    encrypted_private_key = Column(String(4096))
    public_key = Column(String(4096), nullable=True)
