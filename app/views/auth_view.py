from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC

from app.sqlalchemy_models.users_sql import User as SqlUser

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from app.pydantic_models.user_model import User, UserInDB
from app.services.database import sessionmanager, get_db
from app.config import get_config


config = get_config()

secret_key = config['secret_key']
algorithm = config['algorithm']
access_token_expire_minutes = config['access_token_expire_minutes']

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_pasword(submitted_password, hashed_password):
    get_password_hash(submitted_password)
    return pwd_context.verify(submitted_password, hashed_password)


async def get_user_by_username(username: str):
    async with sessionmanager.session() as session:
        try:
            user = await SqlUser.get_user_by_username(session, username)
        except NoResultFound:
            raise ValueError("User not found")
        return user


async def get_user(username: str):
    try:
        user = await get_user_by_username(username)
        return user
    except NoResultFound:
        raise ValueError("User not found")
    return


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        raise ValueError("Incorrect username or password")
    if not verify_pasword(password, user.password):
        raise ValueError("Incorrect username or password")
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key,
                             algorithm=algorithm)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[
                             algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[SqlUser, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if user.disabled:
            raise HTTPException(status_code=401, detail="Inactive user")
        access_token_expires = timedelta(minutes=access_token_expire_minutes)
        access_token = await create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=access_token, token_type="bearer")


@ router.get("/me", response_model=User)
async def get_user_me(current_user: Annotated[SqlUser, Depends(get_current_active_user)]):
    return current_user


class Password(BaseModel):
    password: str


@router.post("/users/{id}/set_auth", response_model=User)
async def set_password(id: int, password: Password, db: AsyncSession = Depends(get_db)):
    # if config['config_name'] != 'testing':
    #     raise HTTPException(status_code=404, detail="Not found")
    try:
        hashed_password = get_password_hash(password.password)
        user = await SqlUser.set_password(db, id, hashed_password)
    except NoResultFound:
        raise HTTPException(status_code=400, detail="User not found")
    return user
