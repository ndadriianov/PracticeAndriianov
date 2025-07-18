from fastapi import FastAPI, HTTPException
from database.db import wait_for_db

from models.flight import Flight
from database.db import SessionDep
from sqlmodel import select

from datetime import datetime as dt


app = FastAPI()


@app.on_event("startup")
def on_startup():
    wait_for_db()


@app.get("/flights/to/{destination}")
async def get_flights_to_destination(destination: str, session: SessionDep):
    flights = session.exec(select(Flight).where(Flight.destination == destination)).all()
    return flights


@app.get("/flights")
async def get_flights(session: SessionDep):
    flights = session.exec(select(Flight)).all()
    return flights


@app.get("/flights/{id}")
async def get_flight(id: int, session: SessionDep):
    flight = session.exec(select(Flight).where(Flight.id == id)).one_or_none()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@app.post("/flights/flight")
async def add_flight(destination: str, price: int, seats_amount: int, date: dt, session: SessionDep):
    flight = Flight(destination=destination, price=price, seats_amount=seats_amount, date=date)
    session.add(flight)
    session.commit()
    session.refresh(flight)