from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text

from ..database import Base


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(128), primary_key=True, index=True)
    user_id = Column(String(128))
    csdek = Column(String(128))
    session_private_key = Column(Text)
    session_token = Column(Text)
    client_id = Column(String(128))
    platform_client_id = Column(String(128))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_at = Column(DateTime, nullable=False)
