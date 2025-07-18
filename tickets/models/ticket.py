from sqlmodel import Field, SQLModel


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    flight_id: int
    seat_number: int
