from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
from supabase import AuthApiError

from auth import supabase, get_current_user

app = FastAPI(
    title="Auth API",
    description="Secure API with Supabase Auth — sign up, log in, log out, and protected routes.",
    version="1.0.0",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail}
    )


class AuthBody(BaseModel):
    email: str
    password: str


@app.get("/")
def root():
    return {"message": "Auth API is running"}


@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", status_code=status.HTTP_200_OK)
def get_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@app.get("/protected/dashboard", status_code=status.HTTP_200_OK)
def get_dashboard(user=Depends(get_current_user)):
    return {
        "message": f"Welcome {user.email}, this is your dashboard.",
        "user_id": user.id,
    }


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


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()
    return None
