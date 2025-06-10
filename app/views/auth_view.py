from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi_camelcase import CamelModel
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security.base import SecurityBase

from app.config import get_config
from app.pydantic_models.user_model import User, FullUser
from app.services.database import get_db, sessionmanager
from app.sqlalchemy_models.user_project_role_sql import User as SqlUser

config = get_config()

secret_key = config["secret_key"]
algorithm = config["algorithm"]
access_token_expire_minutes = config["access_token_expire_minutes"] or 30
refresh_token_expire_minutes = config["refresh_token_expire_minutes"] or 2880
api_prefix = "/api/" + config["api_version"]
tokenUrl = api_prefix + "/auth/token"

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(CamelModel):
    user_data: User
    exp: datetime
    refresh: bool


# TODO: When using the swagger docs interface, the frontend cannot extract the auth token
# The backend needs to detect that it is the swagger interface and provide the correct
# response


class SnakeTokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class CamelTokenResponse(CamelModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class Password(CamelModel):
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_token_user(user: SqlUser):
    user_model = User.model_validate(user)
    return user_model.model_dump(by_alias=True)


class Oath2SchemeUser(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl=tokenUrl)

    async def __call__(self, request: Request):
        try:
            params = await super().__call__(request)
        except Exception as error:
            if error.status_code == 401 and error.detail == "Not authenticated":
                if not config["enforce_authentication"]:
                    async with sessionmanager.session() as db:
                        user = await SqlUser.get(db, config["default_user_id"])
                        user_data = make_token_user(user)
                        params = await create_token(
                            user_data=user_data,
                            token_expire_minutes=access_token_expire_minutes,
                        )
                    return params
            raise error
        return params


oauth2_scheme = Oath2SchemeUser(tokenUrl=tokenUrl)


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_pasword(submitted_password, hashed_password):
    return pwd_context.verify(submitted_password, hashed_password)


async def create_token(
    user_data: dict,
    token_expire_minutes: int,
    refresh_token: bool = False,
):
    to_encode = {"user_data": user_data}
    now = datetime.now(UTC)
    if token_expire_minutes:
        expire = now + timedelta(minutes=token_expire_minutes)
    else:
        expire = now + timedelta(minutes=token_expire_minutes)
    to_encode.update({"exp": expire})
    to_encode.update({"refresh": refresh_token})

    token = Token(**to_encode)
    to_encode_camel = token.model_dump(by_alias=True)

    encoded_jwt = jwt.encode(to_encode_camel, secret_key, algorithm=algorithm)
    return encoded_jwt


async def get_user_by_username(username: str):
    async with sessionmanager.session() as session:
        try:
            user = await SqlUser.get_user_by_username(session, username)
        except NoResultFound:
            raise ValueError("User not found")
        return user


async def get_user_by_email(email: str):
    async with sessionmanager.session() as session:
        try:
            user = await SqlUser.get_user_by_email(session, email)
        except NoResultFound:
            raise ValueError("User not found")
        return user


async def authenticate_user_by_username(username: str, password: str):
    user = await get_user_by_username(username)
    if not user:
        raise ValueError("Incorrect username or password")
    if not verify_pasword(password, user.password):
        raise ValueError("Incorrect username or password")
    return user


async def authenticate_user_by_email(user_email: str, password: str):
    user = await get_user_by_email(user_email)
    if not user:
        raise ValueError("Incorrect email or password")
    if not verify_pasword(password, user.password):
        raise ValueError("Incorrect email or password")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        received_token = Token(**payload)
        user_data = received_token.user_data
        ## check if token has user data
        user_email = user_data.email
        if user_email is None:
            raise credentials_exception
        token_user = await get_user_by_email(user_email)
        if token_user is None:
            raise credentials_exception

        ## check if token is expired
        # expiry_datetime = datetime.fromtimestamp(payload.get("exp"), UTC)
        # if datetime.now(UTC) >= expiry_datetime:
        #     raise InvalidTokenError

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_user


async def get_current_user_with_roles(
    user: Annotated[SqlUser, Depends(get_current_user)],
    request: Request,
):

    user_projects = [project.id for project in user.projects]
    project_id = request.query_params.get("project_id")
    if project_id is None:
        project_id = request.path_params.get("project_id")
    if project_id is not None:
        try:
            check_id = int(project_id)
            if check_id not in user_projects:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User does not have access to this project",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid project id",
            )
    return user


async def get_current_active_user(
    current_user: Annotated[SqlUser, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    return current_user


async def verify_token(request: Request):
    authorization = request.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)
    if not (authorization and scheme and credentials):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
        )
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
        )
    try:
        payload = jwt.decode(credentials, secret_key, algorithms=[algorithm])
        received_token = Token(**payload)
        user_data = received_token.user_data
        email = user_data.email
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
            )
        expiry = datetime.fromtimestamp(payload.get("exp"), UTC)
        if datetime.now(UTC) >= expiry:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session expired",
            )
        user_data_for_token = user_data.model_dump(by_alias=True)
        new_access_token = await create_token(
            user_data=user_data_for_token,
            token_expire_minutes=access_token_expire_minutes,
            refresh_token=False,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    return new_access_token


## TODO: use pyargon2-cffi to generate password hash and verify password


@router.post("/refresh")
async def get_fresh_access_token(
    token: Annotated[str, Depends(verify_token)] = None,
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    return {"access_token": token, "accessToken": token}


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
) -> CamelTokenResponse | SnakeTokenResponse:
    requester = request.headers.get("origin")
    try:
        user = await authenticate_user_by_email(
            form_data.username.lower(), form_data.password
        )
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")
        user_data = make_token_user(user)
        access_token = await create_token(
            user_data=user_data,
            token_expire_minutes=access_token_expire_minutes,
        )
        refresh_token = await create_token(
            user_data=user_data,
            token_expire_minutes=refresh_token_expire_minutes,
            refresh_token=True,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if requester == "http://localhost:8000":
        return SnakeTokenResponse(
            access_token=access_token, token_type="Bearer", refresh_token=refresh_token
        )
    return CamelTokenResponse(
        access_token=access_token, token_type="Bearer", refresh_token=refresh_token
    )


@router.get("/me", response_model=FullUser)
async def get_user_me(
    current_user: Annotated[SqlUser, Depends(get_current_active_user)],
):
    return current_user


@router.post("/set_auth", response_model=dict)
async def set_password(
    password: Password,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    # if config['config_name'] != 'testing':
    #     raise HTTPException(status_code=404, detail="Not found")
    try:
        hashed_password = get_password_hash(password.password)
        user = await SqlUser.set_password(
            db, current_user.id, hashed_password, current_user.id
        )
    except NoResultFound:
        raise HTTPException(status_code=400, detail="User not found")
    return {"detail": "success"}


@router.get("/items")
async def read_items(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    return {"token": token}


@router.post("/verify")
async def verify_email_token(token: Annotated[str, Depends(oauth2_scheme)]):
    if token:
        return {"token": "verified"}


@router.get(
    "/password-token/{id:int}",
    response_model=CamelTokenResponse,
    response_model_exclude_unset=True,
)
async def get_password_token(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[SqlUser, Depends(get_current_user)] = None,
):
    try:
        user = await SqlUser.get(db, id)
        user_data = make_token_user(user)
        password_token = await create_token(
            user_data=user_data,
            token_expire_minutes=access_token_expire_minutes,
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"access_token": password_token, "token_type": "Bearer"}
