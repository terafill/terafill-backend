# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func

# from database import Base


# class PasswordHistory(Base):
#     __tablename__ = "password_history"
#     id = Column(Integer, primary_key=True, index=True)
#     date_created = Column(DateTime(timezone=True), server_default=func.now())
#     password_hash = Column(String(128))
#     item_id = Column(Integer, ForeignKey("items.id"))

#     item = relationship("Item", back_populates="history")
