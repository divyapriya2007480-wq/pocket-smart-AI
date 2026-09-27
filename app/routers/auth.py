from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Token
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(tags=["authentication"])


def normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/register")
def register(
    request: Request,
    name: Annotated[str, Form(min_length=2, max_length=100)],
    email: Annotated[str, Form(min_length=5, max_length=320)],
    password: Annotated[str, Form(min_length=8, max_length=128)],
    db: Session = Depends(get_db),
):
    normalized = normalize_email(email)
    existing = db.scalar(
        select(User).where(func.lower(User.email) == normalized)
    )

    if existing:
        return RedirectResponse(
            "/register?error=An+account+with+that+email+already+exists",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = User(
        name=name.strip(),
        email=normalized,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(
        "/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/login")
def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    normalized = normalize_email(email)
    user = db.scalar(
        select(User).where(func.lower(User.email) == normalized)
    )

    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(
            "/login?error=Invalid+email+or+password",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not user.is_active:
        return RedirectResponse(
            "/login?error=This+account+is+inactive",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse(
        "/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        "/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/token", response_model=Token)
def issue_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    normalized = normalize_email(form.username)
    user = db.scalar(
        select(User).where(func.lower(User.email) == normalized)
    )

    if (
        not user
        or not user.is_active
        or not verify_password(form.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token({"sub": str(user.id)}), token_type="bearer")
