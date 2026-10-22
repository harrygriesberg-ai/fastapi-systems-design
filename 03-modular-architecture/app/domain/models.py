from dataclasses import dataclass


@dataclass(slots=True)
class Product:
    id: int
    name: str
    price: float
    active: bool = True
