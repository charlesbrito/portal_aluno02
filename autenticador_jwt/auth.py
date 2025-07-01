from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import User, Aluno, Professor, Matricula, Admin
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv(override=True)


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    ocupacao: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        ocupacao=create_user_request.ocupacao,
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    if create_user_model.ocupacao == "aluno":
        aluno = Aluno(usuario_id=create_user_model.id)
        db.add(aluno)
        db.commit()

        matricula = Matricula(aluno_id=aluno.id)
        db.add(matricula)
        db.commit()

    elif create_user_model.ocupacao == "professor":
        professor = Professor(usuario_id=create_user_model.id)
        db.add(professor)
        db.commit()

    elif create_user_model.ocupacao == "admin":
        admin = Admin(usuario_id=create_user_model.id)
        db.add(admin)
        db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação de usuário falhou.",
        )
    token = create_access_token(
        user.username, user.id, user.ocupacao, timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, ocupacao: str, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "ocupacao": ocupacao}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        ocupacao: str = payload.get("ocupacao")
        if username is None or user_id is None or ocupacao is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="O usuário não pode ser validado.",
            )
        return {"username": username, "id": user_id, "ocupacao": ocupacao}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="O usuário não pode ser validado.",
        )
