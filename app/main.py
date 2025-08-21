from fastapi import FastAPI
from .database import engine, Base
from .routers import korisnici, frizeri, usluge, termini, recenzije

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(korisnici.router, prefix="/users", tags=["users"])
app.include_router(frizeri.router, prefix="/frizeri", tags=["frizeri"])
app.include_router(usluge.router, prefix="/usluge", tags=["usluge"])
app.include_router(termini.router, prefix="/termini", tags=["termini"])
app.include_router(recenzije.router, prefix="/recenzije", tags=["recenzije"])

@app.get("/")
def read_root():
    return {"message": "FastAPI radi i baza je spremna!"}
