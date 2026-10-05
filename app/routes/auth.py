from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, payload.email, payload.password)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.login_user(db, payload.email, payload.password)
    return LoginResponse(message="Login successful", user_id=user.id, email=user.email)
