from fastapi import FastAPI, HTTPException
from sqlalchemy import func

from database.db import wait_for_db

from models.ticket import Ticket
from database.db import SessionDep
from sqlmodel import select

import requests


app = FastAPI()


@app.on_event("startup")
def on_startup():
    wait_for_db()


@app.get("/tickets")
async def get_ticket_by_id(session: SessionDep):
    ticket = session.exec(select(Ticket)).all()
    return ticket


@app.get("/tickets_by_id/{id}")
async def get_ticket_by_id(id: int, session: SessionDep):
    ticket = session.exec(select(Ticket).where(Ticket.id == id)).one()
    return ticket


@app.get("/tickets_by_name/{name}")
async def get_tickets_by_name(name: str, session: SessionDep):
    tickets = session.exec(select(Ticket).where(Ticket.name == name)).all()
    return tickets


@app.post("/tickets/buy")
async def buy_ticket(flight_id: int, name: str, session: SessionDep):
    resp = requests.get(f"http://flights:8000/flights/{flight_id}", timeout=5)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Flight not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Flight service error")

    flight_data = resp.json()
    seats_total: int = flight_data["seats_amount"]

    sold_stmt = (
        select(func.count())
        .select_from(Ticket)
        .where(Ticket.flight_id == flight_id)
    )
    sold: int = session.exec(sold_stmt).one()

    if sold >= seats_total:
        raise HTTPException(status_code=400, detail="No seats left on this flight")

    seat_number = sold + 1
    ticket = Ticket(name=name, flight_id=flight_id, seat_number=seat_number)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket