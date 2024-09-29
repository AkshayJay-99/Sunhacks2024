from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import timedelta
from utils import hash_password, verify_password
from auth import create_access_token
from models import UserCreate
from database import db, serialize_dict, users_collection
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
    # Check if the user is already in the database
    user_in_db = users_collection.find_one({"email": user.email})
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Hash the password before storing it
    hashed_password = hash_password(user.password)
    
    # Create a dictionary to insert into the database
    user_dict = {"email": user.email, "hashed_password": hashed_password}
    
    # Insert the new user into the users collection
    users_collection.insert_one(user_dict)
    
    return {"msg": "User registered successfully"}

# Login endpoint
@app.post("/login/")
def login(user: UserCreate):
    # Fetch the user from the database by email
    user_in_db = users_collection.find_one({"email": user.email})
    
    # If the user doesn't exist or the password is incorrect, raise an exception
    if not user_in_db or not verify_password(user.password, user_in_db['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # If credentials are valid, create an access token
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
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the user's email from the token payload
        email: str = payload.get("sub", None)
        
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch the user from the database
    user = users_collection.find_one({"email": email})
    
    if user is None:
        raise credentials_exception
    
    # Return the user data in a serializable format
    return serialize_dict(user)
