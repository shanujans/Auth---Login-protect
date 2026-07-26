from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from supabase import AuthApiError

from auth import supabase

app = FastAPI(title="Auth API")


class AuthBody(BaseModel):
    email: str
    password: str


@app.get("/")
def root():
    return {"message": "Auth API is running"}


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(body: AuthBody):
    if not body.email or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    try:
        response = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
        return {"user": response.user}
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(body: AuthBody):
    if not body.email or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
        )
