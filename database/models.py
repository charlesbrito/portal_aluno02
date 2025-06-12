from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from database.database import base
from sqlalchemy.orm import relationship
import random


# Criação da tabela de usuários
class User(base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    ocupacao = Column(String, nullable=False)
    hashed_password = Column(String(255))

    aluno = relationship("Aluno", back_populates="usuario", uselist=False)
    professor = relationship("Professor", back_populates="usuario", uselist=False)


class Aluno(base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)

    usuario = relationship("Usuario", back_populates="aluno")
    matriculas = relationship("Matricula", back_populates="aluno")


class Professor(base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)

    usuario = relationship("Usuario", back_populates="professor")


class Matricula(base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"))

    aluno = relationship("Aluno", back_populates="matriculas")

    def __init__(self, aluno_id):
        self.aluno_id = aluno_id
        self.numero = self.gerar_numero_matricula()

    def gerar_numero_matricula(self):
        return f"M-{random.randint(100000, 999999)}"
