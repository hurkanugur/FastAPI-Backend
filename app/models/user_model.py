from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key, unique identifier for the user.
        email (str): User's email, must be unique.
        hashed_password (str): Hashed password for authentication.
        full_name (str): User's full name.
        created_at (datetime): Timestamp when the user was created, automatically set by the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
