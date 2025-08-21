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

@router.get("/", response_model=list[schemas.UslugaOut])
def get_usluge(db: Session = Depends(get_db)):
    # Pokušaj dohvatiti iz Redis cache-a
    cached = r.get("sve_usluge")
    if cached:
        return json.loads(cached)

    # Ako nema u cache-u, dohvat iz baze
    usluge = db.query(models.Usluga).all()
    result = [schemas.UslugaOut.from_orm(u).dict() for u in usluge]

    # Spremi u Redis na 60 sekundi
    r.setex("sve_usluge", 60, json.dumps(result))
    return result

@router.get("/{usluga_id}", response_model=schemas.UslugaOut)
def get_usluga(usluga_id: int, db: Session = Depends(get_db)):
    usluga = db.query(models.Usluga).get(usluga_id)
    if not usluga:
        raise HTTPException(status_code=404, detail="Usluga nije pronađena")
    return usluga

@router.post("/", response_model=schemas.UslugaOut)
def create_usluga(usluga: schemas.UslugaCreate, db: Session = Depends(get_db)):
    new_usluga = models.Usluga(**usluga.dict())
    db.add(new_usluga)
    db.commit()
    db.refresh(new_usluga)
    return new_usluga

@router.put("/{usluga_id}", response_model=schemas.UslugaOut)
def update_usluga(usluga_id: int, usluga_data: schemas.UslugaCreate, db: Session = Depends(get_db)):
    usluga = db.query(models.Usluga).get(usluga_id)
    if not usluga:
        raise HTTPException(status_code=404, detail="Usluga nije pronađena")
    for key, value in usluga_data.dict().items():
        setattr(usluga, key, value)
    db.commit()
    db.refresh(usluga)
    return usluga

@router.delete("/{usluga_id}")
def delete_usluga(usluga_id: int, db: Session = Depends(get_db)):
    usluga = db.query(models.Usluga).get(usluga_id)
    if not usluga:
        raise HTTPException(status_code=404, detail="Usluga nije pronađena")
    db.delete(usluga)
    db.commit()
    return {"message": "Usluga obrisana"}
