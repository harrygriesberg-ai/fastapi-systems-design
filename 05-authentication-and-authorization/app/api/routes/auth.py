from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserResponse,
)
from app.services.auth import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        return AuthService(db).register(payload)
    except AuthError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/login", response_model=TokenPair)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenPair:
    try:
        return AuthService(db).login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(401, str(exc)) from exc


@router.post("/refresh", response_model=TokenPair)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenPair:
    try:
        return AuthService(db).refresh(payload.refresh_token)
    except AuthError as exc:
        raise HTTPException(401, str(exc)) from exc
