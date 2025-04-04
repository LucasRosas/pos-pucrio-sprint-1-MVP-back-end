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
    players: int = Field(gt=0, description="Número de jogadores deve ser maior que 0", example=1)
    datetime: str = Field(example="2025-04-08T11:00:00.000Z")

class ScheduleSchemaPatch(BaseModel):
    """ Define como um novo schedule a ser editado deve ser representado
    """
    token: str  = Field(example="473b4033-ea29-4a3e-af99-80883d7a2f0e")
    id: str
    players: int = Field(gt=0, description="Número de jogadores deve ser maior que 0", example=2 )
    datetime: str = Field(example="2025-04-08T13:00:00.000Z")
    
class ScheduleSchemaDelete(BaseModel):
    """ Define como um novo schedule a ser deletado deve ser representado
    """   
    token: str = Field(example="473b4033-ea29-4a3e-af99-80883d7a2f0e")
    id: str


class ScheduleSchemaSearch(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base na data da reserva.
    """
    month: int = Field(gt=0, le=12, description="Mês deve ser maior que 0 e menor que 13", example=3)
    year: int = Field(example=2025)
    token: str = Field(example="473b4033-ea29-4a3e-af99-80883d7a2f0e")

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


