from sqlalchemy import Column, String, Text, CHAR

from ..database import Base


class EncryptionKey(Base):
    __tablename__ = "encryption_keys"
    user_id = Column(CHAR(36), primary_key=True)
    item_id = Column(CHAR(36), primary_key=True)
    encrypted_encryption_key = Column(Text, nullable=False)
