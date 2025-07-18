from datetime import datetime as dt
from sqlmodel import Field, SQLModel


class Flight(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    destination: str
    price: int
    seats_amount: int
    date: dt