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

@router.get("/", response_model=list[schemas.FrizerOut])
def get_frizeri(db: Session = Depends(get_db)):
    # Pokušaj dohvatiti iz Redis cache-a
    cached = r.get("svi_frizeri")
    if cached:
        return json.loads(cached)
    
    # Ako nema u cache-u, dohvat iz baze
    frizeri = db.query(models.Frizer).all()
    result = [schemas.FrizerOut.from_orm(f).dict() for f in frizeri]
    
    # Spremi u Redis na 60 sekundi
    r.setex("svi_frizeri", 60, json.dumps(result))
    return result

@router.post("/", response_model=schemas.FrizerOut)
def create_frizer(frizer: schemas.FrizerCreate, db: Session = Depends(get_db)):
    new_frizer = models.Frizer(**frizer.dict())
    db.add(new_frizer)
    db.commit()
    db.refresh(new_frizer)
    return new_frizer

@router.get("/{frizer_id}", response_model=schemas.FrizerOut)
def get_frizer(frizer_id: int, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    return frizer

@router.put("/{frizer_id}", response_model=schemas.FrizerOut)
def update_frizer(frizer_id: int, frizer_data: schemas.FrizerCreate, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    for key, value in frizer_data.dict().items():
        setattr(frizer, key, value)
    db.commit()
    db.refresh(frizer)
    return frizer

@router.delete("/{frizer_id}")
def delete_frizer(frizer_id: int, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    db.delete(frizer)
    db.commit()
    return {"message": "Frizer obrisan"}
