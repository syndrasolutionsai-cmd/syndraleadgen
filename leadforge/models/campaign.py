import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from leadforge.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    niche: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value_prop: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    batch_size: Mapped[int] = mapped_column(Integer, default=500)
    review_pct: Mapped[float] = mapped_column(Float, default=15.0)
    icp_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    scraping_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    personalization_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    verification_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    pipeline_status: Mapped[str] = mapped_column(String(20), default="idle", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    client: Mapped["Client"] = relationship("Client", back_populates="campaigns")
    prospects: Mapped[list["Prospect"]] = relationship("Prospect", back_populates="campaign")
