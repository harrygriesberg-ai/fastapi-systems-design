from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    price: float = Field(gt=0, le=1_000_000)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    active: bool
