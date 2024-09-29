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
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import random

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Instantiate FastAPI app
app = FastAPI()

# openai.api_key = "sk-h6TtCNS3fGaHLw4H5FEZ7t3DlZmNgZcDUvgfcraHliT3BlbkFJcDgBvFZqZ2lazKqRDo36p_UgbnGk_59IyOTFeOOWkA"

client = OpenAI(
    api_key="sk-h6TtCNS3fGaHLw4H5FEZ7t3DlZmNgZcDUvgfcraHliT3BlbkFJcDgBvFZqZ2lazKqRDo36p_UgbnGk_59IyOTFeOOWkA"
)


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

@app.get("/users/me", response_class=HTMLResponse)
async def prompt_page(request: Request):
    return templates.TemplateResponse("response1.html", {"request": request})



# Predefined list of LeetCode-style questions and sample verbal approaches
questions = [
    "FIRST BAD VERSION: Implement a function to find the first bad version in a series of versions.",
    "TWO SUM: Given an array of integers, return indices of the two numbers that add up to a specific target.",
    "MERGE INTERVALS: Given a collection of intervals, merge all overlapping intervals.",
    "LONGEST PALINDROMIC SUBSTRING: Find the longest palindromic substring in a given string.",
    "FIND MEDIAN FROM DATA STREAM: Continuously add numbers and return the median after each addition."
]


@app.post("/generate_feedback")
async def generate_feedback(request: Request):
    try:
        # Parse the incoming JSON data from the request body
        data = await request.json()
        question = data.get("question", random.choice(questions))  # Use provided question or a random one
        verbal_approach = data.get("verbal_approach")

        if not verbal_approach:
            return {"error": "Verbal approach is required"}

        # Prepare messages for the OpenAI API using the correct format
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are an AI interviewer conducting a coding interview."},
            {"role": "system", "content": f"The following LeetCode question was displayed to the candidate: {question}"},
            {
                "role": "system",
                "content": """
                The candidate has explained their approach to solving the problem.

                Please assess the candidate's verbal approach based on the following:

                1) Is their approach correct? If not, provide gentle hints to guide them in the right direction.
                2) What data structures are they using, and suggest how they could have solved that question in a better way.
                3) In the end, give unbiased and specific feedback on improving their approach if necessary.

                Do not say things in bullet points or mention the criteria for assessment (e.g., '**Correctness**:...'). Just share the feedback upfront directly.
                """
            },
            {"role": "user", "content": f"Candidate's Verbal Approach: {verbal_approach}"}
        ]

        # Call OpenAI's chat completion API using the client
        response = client.chat.completions.create(
            model="gpt-4",  # Use gpt-4 or gpt-3.5-turbo
            messages=messages,
            max_tokens=400
        )

        # Extract feedback from the OpenAI response
        if response.choices and response.choices[0].message:
            feedback = response.choices[0].message.content
            if feedback:
                feedback = feedback.strip()  # Only strip if content exists
            else:
                feedback = "No feedback returned from OpenAI."
        else:
            feedback = "No valid response received from OpenAI."
        return {
            "question": question,
            "verbal_approach": verbal_approach,
            "feedback": feedback
        }

    except Exception as e:
        return {"error": str(e)}