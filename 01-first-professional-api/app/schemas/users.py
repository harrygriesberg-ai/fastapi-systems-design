from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=200)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=200)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
