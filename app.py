from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from model import Session, User, Schedule
from logger import logger
from schemas import *
from flask_cors import CORS

import calendar
from datetime import datetime

info = Info(title="Reserver - API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
user_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
schedule_tag = Tag(name="Comentario", description="Adição de um comentário à um produtos cadastrado na base")

@app.cli.command("seed")
def seed():
    """Adiciona usuários à base de dados
    """
    session = Session()
    # adicionando usuários

    hashed_password = generate_password_hash("654321")
    user1 = User(name="Luana Silva", role="student", avatar="https://plus.unsplash.com/premium_vector-1718403156971-7c57ef07337c?q=80&w=1480&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", email="luanasilva", password=hashed_password)

    hashed_password = generate_password_hash("123456")
    user2 = User(name="José Ferreira", role="student", avatar="https://plus.unsplash.com/premium_vector-1718403156893-03d290049a03?q=80&w=1480&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", email="joseferreira", password=hashed_password)

    session.add(user1)
    session.add(user2)
    session.commit()

    schedule1 = Schedule(user=user1.id, players=4, datetime=datetime(2025, 3, 10, 15, 0))
    schedule2 = Schedule(user=user2.id, players=5, datetime=datetime(2025, 3, 10, 16, 0))

    session.add(schedule1)
    session.add(schedule2)
    session.commit()
    print("Dados inseridos com sucesso!")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/login', tags=[user_tag],
          responses={"200": UserViewSchema, "404": ErrorSchema, "401": ErrorSchema})
def login(form: LoginSchema):
    """Faz o login do usuário
    Retorna uma representação do usuario.

    Args:
        form (LoginSchema): dicionário contendo email (string de login) e passowrd do usuário
    
    Returns:
        dict: Retorna uma representação do usuário seguindo o schema definido em UserViewSchema.
    """
    user_email = form.email
    user_password = form.password
    logger.debug(f"Coletando dados sobre usuário #{user_email}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    user = session.query(User).filter(User.email == user_email).first()
    
    if not user:
        # se o produto não foi encontrado
        error_msg = "Usuário não encontrado na base :/"
        logger.warning(f"Erro ao buscar usuário '{user_email}', {error_msg}")
        return {"mesage": error_msg}, 404
    
    if not check_password_hash(user.password, user_password):
        error_msg = "E-mail ou senha inválidos :/"
        logger.warning(f"Erro ao buscar usuário '{user_email}', {error_msg}")
        return {"mesage": error_msg}, 401
    
    logger.debug(f"Usuário econtrado: '{user.email}'")
    # retorna a representação de produto
    return show_user(user), 200

@app.get('/schedules', tags=[schedule_tag],
         responses={"200": ListagemSchedulesSchema, "404": ErrorSchema})
def get_schedules(query: ScheduleBuscaSchema):
    """Faz a busca por todos os Schedule cadastrados no mês e ano informados. O token é utilizado para verificar se o usuário é o dono da reserva.
    Args:
        query (ScheduleBuscaSchema): dicionário contendo month (int) e year (int) e token (int) do usuário.
    Returns:
        dict: Representação da listagem de schedules.
    """
    month = f"{query.month:02d}"
    year = query.year
    userId = query.token

    _, last_day = calendar.monthrange(year, int(month))
    start_date = datetime(year,int(month), 1,0,0,0) 
    end_date = datetime(year, int(month), last_day, 23,59,59)

    logger.debug(f"Coletando schedules ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca por data e por usuário
    schedules = session.query(Schedule).filter(
        Schedule.datetime >= start_date, 
        Schedule.datetime <= end_date
        ).all()
    print(schedules)
   
    
    logger.debug(f"%d schedules econtrados" % len(schedules))
    # Retorna uma representação do schedule seguindo o schema definido em ScheduleViewSchema.
    return show_schedule(schedules, userId), 200

@app.post('/schedule', tags=[schedule_tag],
          responses={"200": ScheduleViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_schedule(form: ScheduleSchema):
    """Adiciona um novo Schedule à base de dados
    Args: 
        form (ScheduleSchema): dicionário contendo token (str), players (int) e datetime (str) da reserva.
    Returns:
        dict: Retorna uma representação do schedule seguindo o schema definido em ScheduleViewSchema.
    """
    user_id = form.token
    players = form.players
    # form.datetime in ISOString 2025-03-11T00:14:00.000Z
    date = datetime.strptime(form.datetime, "%Y-%m-%dT%H:%M:%S.%fZ")



    logger.debug(f"Adicionando schedule de data: '{date}'")
    schedule = Schedule(user=user_id, players=players, datetime=date)
    try:
        # criando conexão com a base
        session = Session()
        # adicionando schedule
        session.add(schedule)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado schedule de data: '{date}'")
        return show_schedule([schedule], user_id), 200

    except IntegrityError as e:
        error_msg = "Já existe uma reserva nessa data :/"
        logger.warning(f"Erro ao adicionar schedule '{date}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar schedule '{datetime}', {error_msg}, {e}")
       
        return {"mesage": error_msg}, 400
    
@app.patch('/schedule', tags=[schedule_tag],
          responses={"200": ScheduleViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def update_schedule(form: ScheduleSchemaPatch):
    """Atualiza um Schedule à base de dados
    Retorna uma representação dos schedules.
    Args:
        form (ScheduleSchemaPatch): dicionário contendo token (str), id (str), players (int) e datetime (str) da reserva.
    Returns:
        dict: Retorna uma representação do schedule seguindo o schema definido em ScheduleViewSchema.
    """
    schedule_id = form.id
    players = form.players
    # form.datetime in ISOString 2025-03-11T00:14:00.000Z
    date = datetime.strptime(form.datetime, "%Y-%m-%dT%H:%M:%S.%fZ")

    logger.debug(f"Atualizando schedule de data: '{date}'")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    schedule = session.query(Schedule).filter(Schedule.id == schedule_id).first()

    if not schedule:
        # se o produto não foi encontrado
        error_msg = "Schedule não encontrado na base :/"
        logger.warning(f"Erro ao buscar schedule '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    
    if not schedule.user == form.token:
        error_msg = "Usuário não autorizado para atualizar schedule :/"
        logger.warning(f"Erro ao atualizar schedule '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 400

    schedule.players = players
    schedule.datetime = date
    session.commit()
    logger.debug(f"Atualizado schedule de data: '{date}'")
    return show_schedule([schedule], schedule.user), 200

# @app.delete('/produto', tags=[produto_tag],
#             responses={"200": ProdutoDelSchema, "404": ErrorSchema})
# def del_produto(query: ProdutoBuscaSchema):
#     """Deleta um Produto a partir do nome de produto informado

#     Retorna uma mensagem de confirmação da remoção.
#     """
#     produto_nome = unquote(unquote(query.nome))
#     print(produto_nome)
#     logger.debug(f"Deletando dados sobre produto #{produto_nome}")
#     # criando conexão com a base
#     session = Session()
#     # fazendo a remoção
#     count = session.query(Produto).filter(Produto.nome == produto_nome).delete()
#     session.commit()

#     if count:
#         # retorna a representação da mensagem de confirmação
#         logger.debug(f"Deletado produto #{produto_nome}")
#         return {"mesage": "Produto removido", "id": produto_nome}
#     else:
#         # se o produto não foi encontrado
#         error_msg = "Produto não encontrado na base :/"
#         logger.warning(f"Erro ao deletar produto #'{produto_nome}', {error_msg}")
#         return {"mesage": error_msg}, 404


# @app.post('/cometario', tags=[comentario_tag],
#           responses={"200": ProdutoViewSchema, "404": ErrorSchema})
# def add_comentario(form: ComentarioSchema):
#     """Adiciona de um novo comentário à um produtos cadastrado na base identificado pelo id

#     Retorna uma representação dos produtos e comentários associados.
#     """
#     produto_id  = form.produto_id
#     logger.debug(f"Adicionando comentários ao produto #{produto_id}")
#     # criando conexão com a base
#     session = Session()
#     # fazendo a busca pelo produto
#     produto = session.query(Produto).filter(Produto.id == produto_id).first()

#     if not produto:
#         # se produto não encontrado
#         error_msg = "Produto não encontrado na base :/"
#         logger.warning(f"Erro ao adicionar comentário ao produto '{produto_id}', {error_msg}")
#         return {"mesage": error_msg}, 404

#     # criando o comentário
#     texto = form.texto
#     comentario = Comentario(texto)

#     # adicionando o comentário ao produto
#     produto.adiciona_comentario(comentario)
#     session.commit()

#     logger.debug(f"Adicionado comentário ao produto #{produto_id}")

#     # retorna a representação de produto
#     return apresenta_produto(produto), 200


if __name__ == "__main__":
    app.run()