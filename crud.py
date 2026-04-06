from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
import auth
from decimal import Decimal

# --- USER OPERATIONS ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Hash the password before storing it!
    hashed_pwd = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- FINANCIAL RECORD OPERATIONS ---

def create_record(db: Session, record: schemas.RecordCreate, user_id: int):
    db_record = models.FinancialRecord(**record.dict(), user_id=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_records(db: Session, skip: int = 0, limit: int = 100, record_type: str = None, category: str = None):
    query = db.query(models.FinancialRecord)
    
    # Apply filters if provided
    if record_type:
        query = query.filter(models.FinancialRecord.type == record_type)
    if category:
        query = query.filter(models.FinancialRecord.category == category)
        
    return query.offset(skip).limit(limit).all()

def update_record(db: Session, record_id: int, update_data: schemas.RecordUpdate):
    db_record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()
    if not db_record:
        return None
    
    # Update only the fields provided in the request
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_record(db: Session, record_id: int):
    db_record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()
    if db_record:
        db.delete(db_record)
        db.commit()
        return True
    return False

# --- DASHBOARD LOGIC ---

def get_dashboard_data(db: Session):
    # Using SQL aggregation for efficiency
    total_income = db.query(func.sum(models.FinancialRecord.amount)).filter(
        models.FinancialRecord.type == "income"
    ).scalar() or Decimal(0)

    total_expenses = db.query(func.sum(models.FinancialRecord.amount)).filter(
        models.FinancialRecord.type == "expense"
    ).scalar() or Decimal(0)

    category_data = db.query(
        models.FinancialRecord.category,
        func.sum(models.FinancialRecord.amount)
    ).group_by(models.FinancialRecord.category).all()

    recent_activity = db.query(models.FinancialRecord).order_by(
        models.FinancialRecord.date.desc()
    ).limit(5).all()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "category_totals": [{"category": c, "total": t} for c, t in category_data],
        "recent_activity": recent_activity
    }