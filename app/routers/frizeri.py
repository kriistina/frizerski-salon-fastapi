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

# Dohvat svih frizera sa keširanjem
@router.get("/", response_model=list[schemas.FrizerOut])
def get_frizeri(db: Session = Depends(get_db)):
    cached = r.get("svi_frizeri")
    if cached:
        return json.loads(cached)
    
    frizeri = db.query(models.Frizer).all()
    result = [schemas.FrizerOut.from_orm(f).dict() for f in frizeri]
    
    r.setex("svi_frizeri", 60, json.dumps(result))
    return result

# Kreiranje novog frizera
@router.post("/", response_model=schemas.FrizerOut)
def create_frizer(frizer: schemas.FrizerCreate, db: Session = Depends(get_db)):
    new_frizer = models.Frizer(**frizer.dict())
    db.add(new_frizer)
    db.commit()
    db.refresh(new_frizer)

    # Obriši keš jer se lista frizera promijenila
    r.delete("svi_frizeri")

    return new_frizer

# Dohvat frizera po ID-u
@router.get("/{frizer_id}", response_model=schemas.FrizerOut)
def get_frizer(frizer_id: int, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    return frizer

# Ažuriranje frizera
@router.put("/{frizer_id}", response_model=schemas.FrizerOut)
def update_frizer(frizer_id: int, frizer_data: schemas.FrizerCreate, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    for key, value in frizer_data.dict().items():
        setattr(frizer, key, value)
    db.commit()
    db.refresh(frizer)

    # Obriši keš jer se lista frizera promijenila
    r.delete("svi_frizeri")

    return frizer

# Brisanje frizera
@router.delete("/{frizer_id}")
def delete_frizer(frizer_id: int, db: Session = Depends(get_db)):
    frizer = db.query(models.Frizer).get(frizer_id)
    if not frizer:
        raise HTTPException(status_code=404, detail="Frizer nije pronađen")
    db.delete(frizer)
    db.commit()

    # Obriši keš jer se lista frizera promijenila
    r.delete("svi_frizeri")

    return {"message": "Frizer obrisan"}
