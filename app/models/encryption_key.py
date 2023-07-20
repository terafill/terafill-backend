from sqlalchemy import Column, String, Text

from ..database import Base


class EncryptionKey(Base):
    __tablename__ = "encryption_keys"
    user_id = Column(String(128), primary_key=True)
    item_id = Column(String(128), primary_key=True)
    vault_id = Column(String(128), primary_key=True)
    encrypted_encryption_key = Column(Text, nullable=False)
