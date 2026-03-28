import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    instantly_api_key: str | None = None


class ClientRead(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
