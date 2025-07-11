from fastapi import APIRouter, Depends, HTTPException, status
from autenticador_jwt.depends import only_for
from database import models
from validacao.vali_materia_sala_nota import MateriaBase, SalaBase
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(prefix="/admin", tags=["admin"])


# Pegar banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# testar login:
@router.get("/admin")
async def get_admin(user=Depends(only_for(["admin"]))):
    return {"msg": f"Bem-vindo, administrador {user['username']}"}


# Criação de salas de aula:
@router.post("/criarsalas", status_code=status.HTTP_201_CREATED)
async def criar_sala(
    sala: SalaBase, db: db_dependency, user=Depends(only_for(["admin"]))
):
    db_sala = models.Salas(**sala.dict())
    db.add(db_sala)
    db.commit()


# Criação das materias:
@router.post("/criarmaterias", status_code=status.HTTP_201_CREATED)
async def criar_materia(
    sala: MateriaBase, db: db_dependency, user=Depends(only_for(["admin"]))
):
    db_materia = models.Materia(**sala.dict())
    db.add(db_materia)
    db.commit()
