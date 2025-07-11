from pydantic import BaseModel


class MateriaBase(BaseModel):
    nome: str


class SalaBase(BaseModel):
    sala: str


class NotasBase(BaseModel):
    aluno_id: int
    materia_id: int
    nota: float
