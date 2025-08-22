from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Korisnici 
class KorisnikBase(BaseModel):
    ime: str
    email: str

class KorisnikCreate(KorisnikBase):
    lozinka: str

class KorisnikOut(KorisnikBase):
    id: int
    class Config:
        from_attributes = True

# Login / Autentikacija 
class KorisnikLogin(BaseModel):
    email: str
    lozinka: str

# Frizeri 
class FrizerBase(BaseModel):
    ime: str
    prezime: str
    specijalnost: str

class FrizerCreate(FrizerBase):
    pass

class FrizerOut(FrizerBase):
    id: int
    prosjecna_ocjena: float
    class Config:
        from_attributes = True

# Usluge 
class UslugaBase(BaseModel):
    naziv: str
    cijena: int
    trajanje: int

class UslugaCreate(UslugaBase):
    pass

class UslugaOut(UslugaBase):
    id: int
    class Config:
        from_attributes = True

# Termini 
class TerminBase(BaseModel):
    vrijeme: datetime
    korisnik_id: int
    frizer_id: int
    usluga_id: int

class TerminCreate(TerminBase):
    pass

class TerminOut(TerminBase):
    id: int
    class Config:
        from_attributes = True

# Recenzije 
class RecenzijaBase(BaseModel):
    ocjena: int
    komentar: Optional[str] = None
    korisnik_id: int
    frizer_id: int

class RecenzijaCreate(RecenzijaBase):
    pass

class RecenzijaOut(RecenzijaBase):
    id: int
    class Config:
        from_attributes = True
