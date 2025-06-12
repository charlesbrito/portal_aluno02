from fastapi import FastAPI, status, Depends, HTTPException
from autenticador_jwt import auth
from database.database import engine, SessionLocal
from database import models
from autenticador_jwt.auth import get_current_user
from sqlalchemy.orm import Session
from typing import Annotated


app = FastAPI()
app.include_router(auth.router)

models.base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="A autenticação falhou")
    return {"user": user}
