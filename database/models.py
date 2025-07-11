from datetime import date
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Table,
    Float,
)
from database.database import base
from sqlalchemy.orm import relationship
import random


# Tabelas associativas (relações muitos-para-muitos)
professor_sala = Table(
    "professor_sala",
    base.metadata,
    Column("professor_id", Integer, ForeignKey("professores.id"), primary_key=True),
    Column("sala_id", Integer, ForeignKey("salas.id"), primary_key=True),
)

professor_materia = Table(
    "professor_materia",
    base.metadata,
    Column("professor_id", Integer, ForeignKey("professores.id"), primary_key=True),
    Column("materia_id", Integer, ForeignKey("materias.id"), primary_key=True),
)


# Usuários do sistema (aluno, professor ou admin)
class User(base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    ocupacao = Column(String, nullable=False)  # 'aluno', 'professor', 'admin'
    hashed_password = Column(String(255), nullable=False)

    aluno = relationship("Aluno", back_populates="usuario", uselist=False)
    professor = relationship("Professor", back_populates="usuario", uselist=False)
    administrador = relationship("Admin", back_populates="usuario", uselist=False)


class Admin(base):
    __tablename__ = "administradores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    usuario = relationship("User", back_populates="administrador")


# Tabela de alunos
class Aluno(base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    sala_id = Column(Integer, ForeignKey("salas.id"), nullable=True)

    usuario = relationship("User", back_populates="aluno")
    sala = relationship("Salas", back_populates="alunos")
    matriculas = relationship("Matricula", back_populates="aluno")
    info_pessoal = relationship("InfoAluno", back_populates="aluno", uselist=False)
    notas = relationship("Nota", back_populates="aluno")


# Tabela de professores
class Professor(base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    usuario = relationship("User", back_populates="professor")
    salas = relationship(
        "Salas", secondary=professor_sala, back_populates="professores"
    )
    materias = relationship(
        "Materia", secondary=professor_materia, back_populates="professores"
    )
    info = relationship("InfoProfessor", back_populates="professor", uselist=False)
    notas = relationship("Nota", back_populates="professor")


# Tabela de matrículas
class Matricula(base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)

    aluno = relationship("Aluno", back_populates="matriculas")

    def __init__(self, aluno_id):
        self.aluno_id = aluno_id
        self.numero = self.gerar_numero_matricula()

    def gerar_numero_matricula(self):
        return f"M-{random.randint(100000, 999999)}"


# Informações pessoais do aluno
class InfoAluno(base):
    __tablename__ = "info_aluno"

    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), unique=True)

    cpf = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String, nullable=False)
    serie = Column(String, nullable=False)
    nome_pai = Column(String, nullable=True)
    nome_mae = Column(String, nullable=True)

    aluno = relationship("Aluno", back_populates="info_pessoal")


# Informações pessoais do professor
class InfoProfessor(base):
    __tablename__ = "info_professor"

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey("professores.id"), unique=True)

    cpf = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    formacao = Column(String, nullable=True)
    especializacao = Column(String, nullable=True)
    data_nascimento = Column(Date, nullable=False)
    endereco = Column(String, nullable=False)

    professor = relationship("Professor", back_populates="info")


# Tabela de salas
class Salas(base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True)
    sala = Column(String, unique=True, nullable=False)

    professores = relationship(
        "Professor", secondary=professor_sala, back_populates="salas"
    )
    alunos = relationship("Aluno", back_populates="sala")


# Tabela de matérias
class Materia(base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)

    professores = relationship(
        "Professor", secondary=professor_materia, back_populates="materias"
    )
    notas = relationship("Nota", back_populates="materia")


# Tabela de notas
class Nota(base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("professores.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    nota = Column(Float, nullable=False)
    data_lancamento = Column(Date, default=date.today)

    aluno = relationship("Aluno", back_populates="notas")
    professor = relationship("Professor", back_populates="notas")
    materia = relationship("Materia", back_populates="notas")
