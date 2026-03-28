from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from leadforge.database import get_db
from leadforge.models.client import Client
from leadforge.api.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.email == form.username))
    client = result.scalar_one_or_none()
    if not client or not verify_password(form.password, client.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not client.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")
    token = create_access_token(str(client.id))
    return {"access_token": token, "token_type": "bearer"}
