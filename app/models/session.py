from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Boolean, CHAR

from ..database import Base


class Session(Base):
    __tablename__ = "sessions"
    id = Column(CHAR(36), primary_key=True, index=True)
    user_id = Column(CHAR(36))
    client_id = Column(CHAR(36))
    platform_client_id = Column(CHAR(36))

    session_private_key = Column(String(4096))
    session_srp_server_private_key = Column(String(4096))
    session_srp_client_public_key = Column(String(4096))
    session_encryption_key = Column(String(128))
    session_token = Column(String(1024))
    activated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_at = Column(DateTime, nullable=False)
