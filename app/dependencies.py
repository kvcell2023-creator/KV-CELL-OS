from fastapi import Request, HTTPException, status, Depends
from app.auth import verify_session_token
from app.database import get_db_engine

def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("session_token")
        
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação necessária")
        
    user_data = verify_session_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada")
        
    return user_data

def require_role(allowed_roles: list[str]):
    def check_permission(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles and user["role"] != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado para esta função")
        return user
    return check_permission
