from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import date
import re


class InfoProfessor(BaseModel):
    cpf: str
    telefone: str
    email: EmailStr
    formacao: Optional[str]
    especializacao: Optional[str]
    data_nascimento: date
    endereco: str
    salas_ids: List[int]
    materias_ids: List[int]

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

    @field_validator("endereco")
    def validar_endereco(cls, v):
        if len(v.strip()) <= 3:
            raise ValueError("O endereço deve ter mais de 3 caracteres")
        return v.title()

    @field_validator("salas_id")
    def validar_sala(cls, v):
        if len(v.strip()) <= 0:
            raise ValueError("A sala deve ter o id maior que 0")
        return v.title()
