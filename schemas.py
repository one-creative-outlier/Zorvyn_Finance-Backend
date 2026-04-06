from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
import enum

# --- ENUMS ---
class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"

# --- USER SCHEMAS ---

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.viewer

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models

# --- FINANCIAL RECORD SCHEMAS ---

class RecordBase(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    type: TransactionType
    category: str
    date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class RecordOut(RecordBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- DASHBOARD & SUMMARY SCHEMAS ---

class CategoryTotal(BaseModel):
    category: str
    total: Decimal

class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    category_totals: List[CategoryTotal]
    recent_activity: List[RecordOut]

# --- AUTHENTICATION ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None