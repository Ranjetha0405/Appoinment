import os
from datetime import datetime, timedelta
from datatype import Id
from dotenv import load_dotenv
from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = "pentafox@5fox"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5040


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("client_id")
        if not client_id:
            raise credentials_exception
        token_data = Id(id=client_id)
    except JWTError:
        raise credentials_exception
    return token_data.id


async def get_client_id_from_token(request):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = await OAuth2PasswordBearer(tokenUrl='login')(request)
    client_id = verify_access_token(token, credentials_exception)
    return client_id
