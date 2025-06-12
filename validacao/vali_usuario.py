from pydantic import BaseModel, field_validator


class Usuario(BaseModel):
    username: str
    ocupacao: str
    password: str

    @field_validator("username")
    def validate_username(cls, v):
        if len(v.strip()) <= 3:
            raise ValueError("O nome deve ter mais de 3 caracteres")
        return v.title()

    @field_validator("password")
    def validate_password(cls, v):
        if len(v.strip()) <= 7:
            raise ValueError("A senha deve conter no mínimo 8 caracteres")
        return v


user = Usuario(username="Charles", ocupacao="professor", password="12345678")
