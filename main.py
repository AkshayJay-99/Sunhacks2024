# main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from utils import hash_password, verify_password
from auth import create_access_token
from models import UserCreate
from database import db, serialize_dict
from jose import JWTError, jwt

app = FastAPI()

# Registration endpoint
@app.post("/register/")
def register(user: UserCreate):
    user_in_db = db['users'].find_one({"email": user.email})
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    user_dict = {"email": user.email, "hashed_password": hashed_password}
    db['users'].insert_one(user_dict)
    return {"msg": "User registered successfully"}

# Login endpoint
@app.post("/login/")
def login(user: UserCreate):
    user_in_db = db['users'].find_one({"email": user.email})
    if not user_in_db or not verify_password(user.password, user_in_db['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user endpoint
@app.get("/users/me/")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db['users'].find_one({"email": email})
    if user is None:
        raise credentials_exception
    return serialize_dict(user)
