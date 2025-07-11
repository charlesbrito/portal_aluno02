from logging import info
from fastapi import APIRouter, Depends, HTTPException, status
from autenticador_jwt.depends import only_for
from database import models
from validacao.vali_professor import InfoProfessor
from validacao.vali_materia_sala_nota import NotasBase
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(prefix="/professor", tags=["professor"])


# Pegar banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/professor")
async def area_professor(user=Depends(only_for(["professor"]))):
    return {"msg": f"Bem-vindo, professor {user['username']}"}


@router.post("/infoprofessor/", status_code=status.HTTP_200_OK)
async def cadastrar_info_professor(
    dados_professor: InfoProfessor,
    db: db_dependency,
    user=Depends(only_for(["professor"])),
):
    # 1. Buscar professor no banco com base no id do usuário logado
    professor_db = db.query(models.Professor).filter_by(usuario_id=user["id"]).first()

    if not professor_db:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    # 2. Verificar se já existe InfoProfessor para esse professor (evita duplicação)
    if professor_db.info:
        raise HTTPException(
            status_code=400, detail="Informações já cadastradas para esse professor"
        )

    # 3. Criar novo InfoProfessor vinculado ao professor encontrado
    nova_info = models.InfoProfessor(
        cpf=dados_professor.cpf,
        telefone=dados_professor.telefone,
        email=dados_professor.email,
        formacao=dados_professor.formacao,
        especializacao=dados_professor.especializacao,
        data_nascimento=dados_professor.data_nascimento,
        endereco=dados_professor.endereco,
        professor_id=professor_db.id,
    )

    db.add(nova_info)

    # 4. Associar salas
    salas = (
        db.query(models.Salas)
        .filter(models.Salas.id.in_(dados_professor.salas_ids))
        .all()
    )
    if not salas:
        raise HTTPException(status_code=404, detail="Salas não encontradas")
    professor_db.salas = salas

    # 5. Associar matérias
    materias = (
        db.query(models.Materia)
        .filter(models.Materia.id.in_(dados_professor.materias_ids))
        .all()
    )
    if not materias:
        raise HTTPException(status_code=404, detail="Matérias não encontradas")
    professor_db.materias = materias

    db.commit()

    return {"msg": "Informações salvas com sucesso", "id_info": nova_info.id}


@router.post("/lançarnotas/", status_code=status.HTTP_200_OK)
async def lancar_notas(
    dados_nota: NotasBase, db: db_dependency, user=Depends(only_for(["professor"]))
):
    # Verifica se o professor logado existe
    professor = (
        db.query(models.Professor)
        .filter(models.Professor.usuario_id == user["id"])
        .first()
    )
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    # Verificar se o aluno existe
    aluno = (
        db.query(models.Aluno).filter(models.Aluno.id == dados_nota.aluno_id).first()
    )
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Verificar se a materia existe
    materia = (
        db.query(models.Materia)
        .filter(models.Materia.id == dados_nota.materia_id)
        .first()
    )
    if not materia:
        raise HTTPException(status_code=404, detail="Matéria não encotrada")

    # Verificar se o professor ensina essa materia
    if materia not in professor.materias:
        raise HTTPException(status_code=404, detail="Você não leciona essa matéria")

    # lanças notas
    nova_nota = models.Nota(
        aluno_id=dados_nota.aluno_id,
        professor_id=professor.id,
        materia_id=dados_nota.materia_id,
        nota=dados_nota.nota,
    )

    db.add(nova_nota)
    db.commit()

    return {"msg": "Nota lançada com sucesso"}
