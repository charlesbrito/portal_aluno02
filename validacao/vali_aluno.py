from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import date
import re
import datetime


class AlunoBase(BaseModel):
    cpf: str
    telefone: str
    endereco: str
    data_nascimento: date
    email: EmailStr
    serie: str
    sala: str
    nome_pai: str
    nome_mae: str

    @field_validator("cpf")
    def validar_cpf(cls, v):
        cpf = re.sub(r"[^0-9]", "", v)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")

        def calcular_digito(cpf, peso):
            soma = sum(int(digito) * (peso - i) for i, digito in enumerate(cpf))
            resto = soma % 11
            return "0" if resto < 2 else str(11 - resto)

        dv1 = calcular_digito(cpf[:9], 10)
        dv2 = calcular_digito(cpf[:9] + dv1, 11)
        if cpf[-2:] != dv1 + dv2:
            raise ValueError("CPF inválido")
        return cpf

    @field_validator("telefone")
    def validar_telefone(cls, v):
        telefone = re.sub(r"[^0-9]", "", v)
        if not (10 <= len(telefone) <= 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")
        return telefone

    @field_validator("data_nascimento")
    def validar_data_nascimento(cls, v):
        hoje = datetime.date.today()
        idade = hoje.year - v.year - ((hoje.month, hoje.day) < (v.month, v.day))
        if idade < 0 or idade > 120:
            raise ValueError("Data de nascimento inválida")
        return v

    @field_validator("endereco")
    def validar_endereco(cls, v):
        if len(v.strip()) <= 3:
            raise ValueError("O endereço deve ter mais de 3 caracteres")
        return v.title()

    @field_validator("serie")
    def validar_serie(cls, v):
        if len(v.strip()) <= 0:
            raise ValueError("A série deve ter mais de 0 caracteres")
        return v.title()

    @field_validator("sala")
    def validar_sala(cls, v):
        if len(v.strip()) <= 0:
            raise ValueError("A sala deve ter mais de 0 caracteres")
        return v.title()

    @field_validator("nome_pai")
    def validar_nome_pai(cls, v):
        if len(v.strip()) <= 0:
            raise ValueError("O nome do pai deve conter mais que 0 caracteres")
        return v

    @field_validator("nome_mae")
    def validar_nome_mae(cls, v):
        if len(v.strip()) <= 0:
            raise ValueError("O nome da mãe deve ter mais que 0 caracteres")
        return v.title()
