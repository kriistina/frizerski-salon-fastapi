from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.KorisnikOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.Korisnik).all()
    return users

@router.get("/{user_id}", response_model=schemas.KorisnikOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Korisnik).filter(models.Korisnik.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
    return user

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
    return {"message": "Korisnik ažuriran", "user": {"id": db_user.id, "ime": db_user.ime, "email": db_user.email}}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji")
    
    db.delete(db_user)
    db.commit()
    return {"message": f"Korisnik s ID {user_id} je obrisan"}

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
    return {"message": "Registracija uspješna", "user_id": new_user.id}

@router.post("/login")
def login(user: schemas.KorisnikLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.Korisnik).filter(models.Korisnik.email == user.email).first()
    if not db_user or not pwd_context.verify(user.lozinka, db_user.lozinka):
        raise HTTPException(status_code=401, detail="Neispravni podaci")
    return {"message": "Login uspješan", "user_id": db_user.id}
