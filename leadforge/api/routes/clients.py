from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from leadforge.database import get_db
from leadforge.models.client import Client
from leadforge.schemas.client import ClientCreate, ClientRead
from leadforge.api.auth import hash_password
from leadforge.api.deps import get_current_client
from leadforge.crypto import encrypt

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Client).where(Client.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    client = Client(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        instantly_api_key_enc=encrypt(payload.instantly_api_key) if payload.instantly_api_key else None,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/me", response_model=ClientRead)
async def get_me(current: Client = Depends(get_current_client)):
    return current


class ClientUpdate(BaseModel):
    instantly_api_key: str | None = None


@router.patch("/me", response_model=ClientRead)
async def update_me(
    payload: ClientUpdate,
    current: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
):
    if payload.instantly_api_key is not None:
        current.instantly_api_key_enc = encrypt(payload.instantly_api_key) if payload.instantly_api_key else None
    await db.commit()
    await db.refresh(current)
    return current


@router.get("/all", response_model=list[ClientRead])
async def list_all_clients(
    current: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list all client accounts."""
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    return result.scalars().all()
