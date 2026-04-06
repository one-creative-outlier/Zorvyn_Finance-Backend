from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud, auth, database
from database import engine, get_db

# Create the database tables in Neon on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="Backend for financial record management and access control.",
    version="1.0.0"
)

# --- AUTHENTICATION & USER MANAGEMENT ---

@app.post("/login", tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=schemas.UserOut, tags=["Users"])
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# --- FINANCIAL RECORDS (CRUD) ---

# Role-based dependencies
allow_viewer = auth.RoleChecker(["viewer", "analyst", "admin"])
allow_analyst = auth.RoleChecker(["analyst", "admin"])
allow_admin = auth.RoleChecker(["admin"])

@app.post("/records", response_model=schemas.RecordOut, tags=["Records"])
def add_record(
    record: schemas.RecordCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user),
    _ = Depends(allow_analyst)
):
    return crud.create_record(db=db, record=record, user_id=current_user.id)

@app.get("/records", response_model=List[schemas.RecordOut], tags=["Records"])
def read_records(
    skip: int = 0, 
    limit: int = 100, 
    type: str = None, 
    category: str = None,
    db: Session = Depends(get_db),
    _ = Depends(allow_viewer)
):
    return crud.get_records(db, skip=skip, limit=limit, record_type=type, category=category)

@app.put("/records/{record_id}", response_model=schemas.RecordOut, tags=["Records"])
def update_existing_record(
    record_id: int, 
    record_update: schemas.RecordUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(allow_admin)
):
    updated = crud.update_record(db, record_id, record_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated

@app.delete("/records/{record_id}", tags=["Records"])
def delete_existing_record(
    record_id: int, 
    db: Session = Depends(get_db),
    _ = Depends(allow_admin)
):
    if not crud.delete_record(db, record_id):
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Successfully deleted record"}

# --- DASHBOARD SUMMARY ---

@app.get("/dashboard/summary", tags=["Dashboard"])
def get_summary(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user),
    _ = Depends(allow_viewer)
):
    return crud.get_dashboard_data(db)

# --- HEALTH CHECK ---
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "database": "connected"}