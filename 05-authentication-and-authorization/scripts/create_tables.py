from app.db import Base, engine
from app.models.user import User  # noqa: F401


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("tables created")
