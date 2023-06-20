from sqlalchemy import Column, String

from ..database import Base


class MPESK(Base):
    __tablename__ = "mpesk"
    user_id = Column(String(128), primary_key=True, index=True)
    mpesk = Column(String(256))
