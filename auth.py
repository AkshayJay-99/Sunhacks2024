from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt

# Secret key for encoding and algorithm (you should set these values in your actual code)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # Assign default timedelta if None is provided
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)  # Default expiration time

    # Use timezone-aware UTC datetime
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
