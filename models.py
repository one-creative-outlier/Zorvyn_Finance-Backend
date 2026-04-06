from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

# Define Enums for better data integrity in Postgres
class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

class UserRole(enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer") # Stored as string for simpler role checking
    is_active = Column(Boolean, default=True)

    # Relationship: One user can have many financial records
    records = relationship("FinancialRecord", back_populates="owner", cascade="all, delete-orphan")

class FinancialRecord(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False) # Financial precision
    type = Column(String, nullable=False) # 'income' or 'expense'
    category = Column(String, index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    # Foreign Key: Links the record to a specific user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship: Links back to the User object
    owner = relationship("User", back_populates="records")