from sqlalchemy import Column, String
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    google_id = Column(String, unique=True, index=True)
    given_name = Column(String)
    family_name = Column(String)
    locale = Column(String)
