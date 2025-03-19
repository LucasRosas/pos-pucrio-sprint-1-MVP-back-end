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
user_tag = Tag(name="Autenticação", description="Autenticação de usuário")
schedule_tag = Tag(name="Reservas", description="Operações de agendamento")

@app.cli.command("seed")
def seed():
    """Adiciona usuários à base de dados
    """
    session = Session()
    # adicionando usuários

    hashed_password = generate_password_hash("654321")
    user1 = User(name="João Fonseca", role="Aluno", avatar="https://conteudo.imguol.com.br/c/esporte/62/2025/03/03/joao-fonseca-na-primeira-rodada-do-rio-open-de-2025-1741050299448_v2_450x450.jpg.webp", email="joaofonseca", password=hashed_password)

    hashed_password = generate_password_hash("123456")
    user2 = User(name="Beatriz Haddad", role="Aluna", avatar="https://photoresources.wtatennis.com/photo-resources/2024/04/29/440d7a25-7fee-431e-b9ce-2df1804daac3/HaddadMaia-Torso_318176-WTA-Tennis.png?width=950", email="biahaddad", password=hashed_password)

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
    Retorna uma representação do usuário.

    **Args:**
        form (LoginSchema): dicionário contendo email (string de login) e passowrd do usuário
    
    **Returns:**
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
        # se o usuário não foi encontrado
        error_msg = "Credenciais inválidas :/"
        logger.warning(f"Erro ao buscar usuário '{user_email}', {error_msg}")
        return {"mesage": error_msg}, 404
    
    if not check_password_hash(user.password, user_password):
        # se a senha não for a mesma
        error_msg = "E-mail ou senha inválidos :/"
        logger.warning(f"Erro ao buscar usuário '{user_email}', {error_msg}")
        return {"mesage": error_msg}, 401
    
    logger.debug(f"Usuário econtrado: '{user.email}'")
    # retorna a representação de produto
    return show_user(user), 200

@app.get('/schedules', tags=[schedule_tag],
         responses={"200": ScheduleViewSchemaList, "404": ErrorSchema})
def get_schedules(query: ScheduleSchemaSearch):
    """Faz a busca por todas as reservas cadastradas no mês e ano informados. O token é utilizado para verificar se o usuário é o dono da reserva.
    
    **Args:**
        query (ScheduleSchemaSearch): dicionário contendo month (int) e year (int) e token (int) do usuário.

    **Returns:**
        dict: Representação da listagem de reservas.
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
def add_schedule(form: ScheduleSchemaPost):
    """Adiciona uma nova reserva  na base de dados
    
    **Args:** 
        form (ScheduleSchema): dicionário contendo token (str), players (int) e datetime (str) da reserva.
    
    **Returns:**
        dict: Retorna uma representação da reserva seguindo o schema definido em ScheduleViewSchema.
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
    """Atualiza uma reserva na base de dados
    Retorna uma representação das reservas.
    
    **Args:**
        form (ScheduleSchemaPatch): dicionário contendo token (str), id (str), players (int) e datetime (str) da reserva.
    
    **Returns:**
        dict: Retorna uma representação da reserva seguindo o schema definido em ScheduleViewSchema.
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
        # se a reserva não foi encontrada
        error_msg = "Schedule não encontrado na base :/"
        logger.warning(f"Erro ao buscar schedule '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    
    if not schedule.user == form.token:
        # se o usuário não for o dono da reserva
        error_msg = "Usuário não autorizado para atualizar schedule :/"
        logger.warning(f"Erro ao atualizar schedule '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 400

    # caso contrário segue com a atualização
    schedule.players = players
    schedule.datetime = date
    session.commit()
    logger.debug(f"Atualizado schedule de data: '{date}'")
    return show_schedule([schedule], schedule.user), 200

@app.delete('/schedule', tags=[schedule_tag],
             responses={"200": ScheduleViewSchemaDelete, "404": ErrorSchema})
def del_schedule(query: ScheduleSchemaDelete):
    """Deleta uma reserva da base de dados
    Retorna uma mensagem de confirmação da remoção.
    
    **Args**:
        query (ScheduleSchemaDelete): dicionário contendo token (str) e id (str) da reserva.
    
    **Returns:**
        dict: Retorna uma mensagem de confirmação da remoção com o id da reserva deletada.
    """
    schedule_id = query.id
    logger.debug(f"Deletando schedule de id: '{schedule_id}'")
    # criando conexão com a base
    session = Session()
    # fazendo a busca da reserva pelo id
    schedule = session.query(Schedule).filter(Schedule.id == schedule_id).first()

    if not schedule:
        # se a reserva não foi encontrada
        error_msg = "Reserva não encontrada na base :/"
        logger.warning(f"Erro ao buscar reserva '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    
    if not schedule.user == query.token:
        # se o usuário não for o dono da reserva
        error_msg = "Usuário não autorizado para deletar reserva :/"
        logger.warning(f"Erro ao deletar schedule '{schedule_id}', {error_msg}")
        return {"mesage": error_msg}, 400

    # caso contrário segue com a exclusão
    session.delete(schedule)
    session.commit()
    logger.debug(f"Deletado schedule de id: '{schedule_id}'")
    return {"mesage": "Reserva deletada com sucesso!", "id": schedule_id}, 200

if __name__ == "__main__":
    app.run()