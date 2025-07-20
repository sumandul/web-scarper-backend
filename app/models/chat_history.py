# app/models/chat_history.py

import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    scrape_id = Column(UUID(as_uuid=True), ForeignKey("scrape.id"), nullable=False)

    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Optional relationship for easy access
    scrape_job = relationship("ScrapeJob", back_populates="chat_histories")
