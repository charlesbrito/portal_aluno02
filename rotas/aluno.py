from fastapi import APIRouter, Depends, HTTPException, status
from autenticador_jwt.depends import only_for
from database import models
from validacao.vali_aluno import AlunoBase
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(prefix="/area", tags=["area"])


# Pegar banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/alunos")
async def area_aluno(user=Depends(only_for(["aluno"]))):
    return {"msg": f"Bem-vindo, aluno {user['username']}"}


# Criar informações de alunos
@router.post("/infoalunos/", status_code=status.HTTP_200_OK)
async def info_aluno(
    aluno: AlunoBase, db: db_dependency, user=Depends(only_for(["aluno"]))
):
    # 1. Buscar aluno no banco com base no id do usuário logado
    aluno_db = db.query(models.Aluno).filter_by(usuario_id=user["id"]).first()

    if not aluno_db:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # 2. Verificar se já existe InfoAluno para esse aluno (evita duplicação)
    if aluno_db.info_pessoal:
        raise HTTPException(
            status_code=400, detail="Informações já cadastradas para esse aluno"
        )

    # 3. Criar novo InfoAluno vinculado ao aluno encontrado
    info = models.InfoAluno(
        aluno_id=aluno_db.id,
        cpf=aluno.cpf,
        telefone=aluno.telefone,
        endereco=aluno.endereco,
        data_nascimento=aluno.data_nascimento,
        email=aluno.email,
        serie=aluno.serie,
        sala=aluno.sala,
        nome_pai=aluno.nome_pai,
        nome_mae=aluno.nome_mae,
    )

    db.add(info)
    db.commit()
    db.refresh(info)

    return {"msg": "Informações salvas com sucesso", "id_info": info.id}
