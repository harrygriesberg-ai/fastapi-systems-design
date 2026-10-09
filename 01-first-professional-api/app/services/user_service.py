from dataclasses import dataclass

from app.schemas.users import UserCreate, UserResponse, UserUpdate


class UserNotFoundError(Exception):
    pass


@dataclass(slots=True)
class UserRecord:
    id: int
    name: str
    email: str


class UserService:
    def __init__(self) -> None:
        self._users: dict[int, UserRecord] = {}
        self._next_id = 1

    def list_users(self) -> list[UserResponse]:
        return [self._to_response(user) for user in self._users.values()]

    def get_user(self, user_id: int) -> UserResponse:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} was not found")
        return self._to_response(user)

    def create_user(self, payload: UserCreate) -> UserResponse:
        user = UserRecord(id=self._next_id, name=payload.name, email=payload.email)
        self._users[user.id] = user
        self._next_id += 1
        return self._to_response(user)

    def update_user(self, user_id: int, payload: UserUpdate) -> UserResponse:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} was not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return self._to_response(user)

    def delete_user(self, user_id: int) -> None:
        if self._users.pop(user_id, None) is None:
            raise UserNotFoundError(f"User {user_id} was not found")

    @staticmethod
    def _to_response(user: UserRecord) -> UserResponse:
        return UserResponse(id=user.id, name=user.name, email=user.email)
