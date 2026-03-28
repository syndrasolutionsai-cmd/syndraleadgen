import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from leadforge.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(150))
    geography: Mapped[str | None] = mapped_column(String(100))
    enriched_data: Mapped[dict] = mapped_column(JSON, default=dict)
    icp_score: Mapped[float | None] = mapped_column(Float)
    email_verification_score: Mapped[float | None] = mapped_column(Float)
    confirmed_sources: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="prospects")
    email_record: Mapped["Email | None"] = relationship("Email", back_populates="prospect", uselist=False)
