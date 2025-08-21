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

@router.get("/", response_model=list[schemas.RecenzijaOut])
def get_recenzije(db: Session = Depends(get_db)):
    cached = r.get("sve_recenzije")
    if cached:
        return json.loads(cached)

    recenzije = db.query(models.Recenzija).all()
    result = [schemas.RecenzijaOut.from_orm(rz).dict() for rz in recenzije]

    r.setex("sve_recenzije", 60, json.dumps(result))
    return result

@router.get("/{recenzija_id}", response_model=schemas.RecenzijaOut)
def get_recenzija(recenzija_id: int, db: Session = Depends(get_db)):
    recenzija = db.query(models.Recenzija).get(recenzija_id)
    if not recenzija:
        raise HTTPException(status_code=404, detail="Recenzija nije pronađena")
    return recenzija

@router.post("/", response_model=schemas.RecenzijaOut)
def create_recenzija(recenzija: schemas.RecenzijaCreate, db: Session = Depends(get_db)):
    new_recenzija = models.Recenzija(**recenzija.dict())
    db.add(new_recenzija)
    db.commit()
    db.refresh(new_recenzija)
    return new_recenzija

@router.put("/{recenzija_id}", response_model=schemas.RecenzijaOut)
def update_recenzija(recenzija_id: int, recenzija_data: schemas.RecenzijaCreate, db: Session = Depends(get_db)):
    recenzija = db.query(models.Recenzija).get(recenzija_id)
    if not recenzija:
        raise HTTPException(status_code=404, detail="Recenzija nije pronađena")
    for key, value in recenzija_data.dict().items():
        setattr(recenzija, key, value)
    db.commit()
    db.refresh(recenzija)
    return recenzija

@router.delete("/{recenzija_id}")
def delete_recenzija(recenzija_id: int, db: Session = Depends(get_db)):
    recenzija = db.query(models.Recenzija).get(recenzija_id)
    if not recenzija:
        raise HTTPException(status_code=404, detail="Recenzija nije pronađena")
    db.delete(recenzija)
    db.commit()
    return {"message": "Recenzija obrisana"}
