from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from  model import Base, Schedule
import uuid

class User(Base):
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    role = Column(String)
    avatar = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o usuário e schedule.    
    schedule = relationship("Schedule")

    def __init__(self, name:str, role:str, avatar:str, email:str, password:str, created_at:Union[DateTime, None] = None):
        """
        Cria um Usuário

        Arguments:
            name: nome do usuário.
            role: função do usuário (ex: aluno, administrador)
            avatar: avatar do usuário
            email: email do usuário
            password: senha do usuário
            created_at: data de quando o usuário foi inserido à base
        """
        self.name = name
        self.role = role
        self.avatar = avatar
        self.email = email
        self.password = password
        
        # se não for informada, será o data exata da inserção no banco
        if created_at:
            self.created_at = created_at
        
    

    #def adiciona_comentario(self, comentario:Comentario):
    #    """ Adiciona um novo comentário ao Produto
    #    """
    #    self.comentarios.append(comentario)

