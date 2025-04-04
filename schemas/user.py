from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    """ Define como um novo usuario a ser inserido deve ser representado
    """
    id: str
    name: str
    role: str
    avatar: str
    email: str
    password: str
    created_at: str

class LoginSchema(BaseModel):
    """ Define como o login do usuário deve ser representado
    """
    email: str = Field(example="joaofonseca")
    password: str = Field(example="654321")

class UserViewSchema(BaseModel):
    """ Define como um novo usuario a ser inserido deve ser representado
    """
    id: str
    name: str
    role: str
    avatar: str
    created_at: str
    
def show_user(user):
    """ Retorna uma representação do usuário seguindo o schema definido em
        UserViewSchema.
    """
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "avatar": user.avatar,
        "created_at": user.created_at
    }
