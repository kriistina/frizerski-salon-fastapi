from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..redis_client import r
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dohvat svih termina sa keširanjem
@router.get("/", response_model=list[schemas.TerminOut])
def get_termini(db: Session = Depends(get_db)):
    cached = r.get("svi_termini")
    if cached:
        return json.loads(cached)

    termini = db.query(models.Termin).all()
    result = [schemas.TerminOut.from_orm(t).dict() for t in termini]

    r.setex("svi_termini", 60, json.dumps(result))
    return result

# Dohvat termina po ID-u
@router.get("/{termin_id}", response_model=schemas.TerminOut)
def get_termin(termin_id: int, db: Session = Depends(get_db)):
    termin = db.query(models.Termin).get(termin_id)
    if not termin:
        raise HTTPException(status_code=404, detail="Termin nije pronađen")
    return termin

# Kreiranje novog termina
@router.post("/", response_model=schemas.TerminOut)
def create_termin(termin: schemas.TerminCreate, db: Session = Depends(get_db)):
    new_termin = models.Termin(**termin.dict())
    db.add(new_termin)
    db.commit()
    db.refresh(new_termin)

    # Obriši keš jer se lista termina promijenila
    r.delete("svi_termini")

    return new_termin

# Ažuriranje termina
@router.put("/{termin_id}", response_model=schemas.TerminOut)
def update_termin(termin_id: int, termin_data: schemas.TerminCreate, db: Session = Depends(get_db)):
    termin = db.query(models.Termin).get(termin_id)
    if not termin:
        raise HTTPException(status_code=404, detail="Termin nije pronađen")
    for key, value in termin_data.dict().items():
        setattr(termin, key, value)
    db.commit()
    db.refresh(termin)

    # Obriši keš jer se lista termina promijenila
    r.delete("svi_termini")

    return termin

# Brisanje termina
@router.delete("/{termin_id}")
def delete_termin(termin_id: int, db: Session = Depends(get_db)):
    termin = db.query(models.Termin).get(termin_id)
    if not termin:
        raise HTTPException(status_code=404, detail="Termin nije pronađen")
    db.delete(termin)
    db.commit()

    # Obriši keš jer se lista termina promijenila
    r.delete("svi_termini")

    return {"message": "Termin obrisan"}
