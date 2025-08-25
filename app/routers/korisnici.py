from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import SessionLocal
from .. import models, schemas
from ..redis_client import r
import json  

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dohvat svih korisnika sa keširanjem
@router.get("/", response_model=list[schemas.KorisnikOut])
def get_users(db: Session = Depends(get_db)):
    cached = r.get("svi_korisnici")
    if cached:
        return json.loads(cached)
    
    users = db.query(models.Korisnik).all()
    result = [schemas.KorisnikOut.from_orm(u).dict() for u in users]
    
    r.setex("svi_korisnici", 60, json.dumps(result))
    return result

# Dohvat korisnika po ID-u
@router.get("/{user_id}", response_model=schemas.KorisnikOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Korisnik).filter(models.Korisnik.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
    return user

# Ažuriranje korisnika
@router.put("/{user_id}")
def update_user(user_id: int, user: schemas.KorisnikCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji")
    
    db_user.ime = user.ime
    db_user.email = user.email
    db_user.lozinka = pwd_context.hash(user.lozinka)  # hash lozinke
    
    db.commit()
    db.refresh(db_user)

    # Obriši keš jer se lista korisnika promijenila
    r.delete("svi_korisnici")
    
    return {"message": "Korisnik ažuriran", "user": {"id": db_user.id, "ime": db_user.ime, "email": db_user.email}}

# Brisanje korisnika
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji")
    
    db.delete(db_user)
    db.commit()

    # Obriši keš jer se lista korisnika promijenila
    r.delete("svi_korisnici")

    return {"message": f"Korisnik s ID {user_id} je obrisan"}

# Registracija
@router.post("/register")
def register(user: schemas.KorisnikCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email već postoji")
    hashed_password = pwd_context.hash(user.lozinka)
    new_user = models.Korisnik(ime=user.ime, email=user.email, lozinka=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Obriši keš jer se lista korisnika promijenila
    r.delete("svi_korisnici")

    return {"message": "Registracija uspješna", "user_id": new_user.id}

# Login
@router.post("/login")
def login(user: schemas.KorisnikLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.email == user.email).first()
    if not db_user or not pwd_context.verify(user.lozinka, db_user.lozinka):
        raise HTTPException(status_code=401, detail="Neispravni podaci")
    return {"message": "Login uspješan", "user_id": db_user.id}
