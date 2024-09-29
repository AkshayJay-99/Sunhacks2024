from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import timedelta
from utils import hash_password, verify_password
from auth import create_access_token
from models import UserCreate
from database import db, serialize_dict
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Instantiate FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

# Define the OAuth2PasswordBearer scheme, which expects a token from the "Authorization: Bearer" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Loading Landing Page
@app.get("/", response_class=HTMLResponse)
async def read_landing(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
    

# Loading Register Page
@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Loading Login Page
@app.get("/login/", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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
        email: str = payload.get("sub", None)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db['users'].find_one({"email": email})
    if user is None:
        raise credentials_exception
    return serialize_dict(user)
