from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Request
import jwt
from jwt.exceptions import PyJWKError

from app.config import get_config

config = get_config()
secret_key = config["secret_key"]
algorithm = config["algorithm"]


class Authorizations:
    def __init__(self):
        pass

    async def __call__(self, request: Request):
        return "Hallo"
