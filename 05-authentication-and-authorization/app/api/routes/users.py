from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.repositories.users import UserRepository
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return [
        UserResponse(id=user.id, email=user.email, role=user.role)
        for user in UserRepository(db).list()
    ]
