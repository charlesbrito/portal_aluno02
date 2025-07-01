from fastapi import Request, Depends, HTTPException
from autenticador_jwt.auth import get_current_user
from starlette import status


def only_for(ocupacoes: list[str]):
    def verificar_ocupacao(user=Depends(get_current_user)):
        if user["ocupacao"] not in ocupacoes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return user

    return verificar_ocupacao
