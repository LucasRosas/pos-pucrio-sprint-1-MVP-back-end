from pydantic import BaseModel, Field
from typing import Optional, List
from model.schedule import Schedule
from schemas import UserSchema

# input: ScheduleSchema{Action}
# output: ScheduleViewSchema{Action}

class ScheduleSchemaPost(BaseModel):
    """ Define como um novo schedule a ser inserido deve ser representado
    """
    token: str
    players: int = Field(gt=0, description="Número de jogadores deve ser maior que 0" )
    datetime: str

class ScheduleSchemaPatch(BaseModel):
    """ Define como um novo schedule a ser editado deve ser representado
    """
    token: str
    id: str
    players: int = Field(gt=0, description="Número de jogadores deve ser maior que 0" )
    datetime: str
    
class ScheduleSchemaDelete(BaseModel):
    """ Define como um novo schedule a ser deletado deve ser representado
    """   
    token: str 
    id: str


class ScheduleSchemaSearch(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base na data da reserva.
    """
    month: int
    year: int
    token: str

class ScheduleViewSchema(BaseModel):
    """ Define como um schedule será retornado.
    """
    id: str = "sd54sd3f4sdf"
    isMine: bool = True
    players: int = 1
    datetime: str = "2025-03-10 15:00:00"
    created_at: str = "2025-03-05 15:10:00:00"

class ScheduleViewSchemaDelete(BaseModel):
    """ Define como um schedule será deletado.
    """
    message: str = "Reserva deletada com sucesso"
    id: str = "sd54sd3f4sdf"

class ScheduleViewSchemaList(BaseModel):
    """ Define como uma listagem de reservas será retornada.
    """
    schedules: List[ScheduleViewSchema]

def show_schedule(schedules: List[Schedule], user_id: str): 
    """ Retorna uma representação do schedule seguindo o schema definido em ScheduleViewSchema.
    """
    result = []
    for schedule in schedules:
        result.append({
            "id": schedule.id,
            "isMine": schedule.user == user_id,
            "players": schedule.players,
            "datetime": schedule.datetime,
            "created_at": schedule.created_at
        })

    return {"schedules": result}


