from sqlalchemy import Column, String, Text

from ..database import Base


class KeyWrappingKey(Base):
    __tablename__ = "key_wrapping_keys"
    user_id = Column(String(128), primary_key=True, index=True)
    encrypted_private_key = Column(Text)
    public_key = Column(Text, nullable=True)
