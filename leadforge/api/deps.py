import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from leadforge.database import get_db
from leadforge.api.auth import decode_token
from leadforge.models.client import Client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_client(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Client:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        client_id = decode_token(token)
    except (JWTError, ValueError):
        raise credentials_exc

    result = await db.execute(select(Client).where(Client.id == uuid.UUID(client_id)))
    client = result.scalar_one_or_none()
    if client is None or not client.is_active:
        raise credentials_exc
    return client
