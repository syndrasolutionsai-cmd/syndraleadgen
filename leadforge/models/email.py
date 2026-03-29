import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float, Text, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from leadforge.database import Base


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    icebreaker: Mapped[str] = mapped_column(Text, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_text: Mapped[str] = mapped_column(Text, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[EmailStatus] = mapped_column(SAEnum(EmailStatus), default=EmailStatus.PENDING)
    instantly_lead_id: Mapped[str | None] = mapped_column(String(255))
    opened: Mapped[bool] = mapped_column(Boolean, default=False)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    replied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="email_record")
