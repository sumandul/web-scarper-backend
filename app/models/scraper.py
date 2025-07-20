from sqlalchemy import Column, String, Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base
from sqlalchemy.orm import relationship
import uuid

class ScrapeJob(Base):
    __tablename__ = "scrape"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    scraper_type = Column(String, nullable=False)
    raw_html = Column(Text)
    llm_summary = Column(Text)
    headline = Column(Text)
    tldr = Column(Text)
    topics = Column(JSON)
    seo_tags = Column(JSON)
    entities = Column(JSON)
    sentiment = Column(JSON)
    tags = Column(JSON)
    status = Column(String)
    result = Column(JSON)
    created_at = Column(String)  # consider DateTime with func.now()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationship to ChatHistory
    chat_histories = relationship("ChatHistory", back_populates="scrape_job", cascade="all, delete-orphan")
