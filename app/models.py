from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Float

from .database import Base

class Korisnik(Base):
    __tablename__ = "korisnici"
    id = Column(Integer, primary_key=True, index=True)
    ime = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    lozinka = Column(String(255), nullable=False)

    recenzije = relationship("Recenzija", back_populates="korisnik")
    termini = relationship("Termin", back_populates="korisnik")

class Frizer(Base):
    __tablename__ = "frizeri"
    id = Column(Integer, primary_key=True, index=True)
    ime = Column(String(50), nullable=False)
    prezime = Column(String(50), nullable=False)
    specijalnost = Column(String(100), nullable=False)
    prosjecna_ocjena = Column(Float, default=0)  # nova kolona

    termini = relationship("Termin", back_populates="frizer", cascade="all, delete-orphan")
    recenzije = relationship("Recenzija", back_populates="frizer",cascade="all, delete-orphan")


class Usluga(Base):
    __tablename__ = "usluge"
    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(100), nullable=False)
    cijena = Column(Integer, nullable=False)
    trajanje = Column(Integer, nullable=False)  

    termini = relationship("Termin", back_populates="usluga")

class Termin(Base):
    __tablename__ = "termini"
    id = Column(Integer, primary_key=True, index=True)
    vrijeme = Column(DateTime)
    korisnik_id = Column(Integer, ForeignKey("korisnici.id"), nullable=False)
    frizer_id = Column(Integer, ForeignKey("frizeri.id"), nullable=False)
    usluga_id = Column(Integer, ForeignKey("usluge.id"), nullable=False)

    korisnik = relationship("Korisnik", back_populates="termini")
    frizer = relationship("Frizer", back_populates="termini")
    usluga = relationship("Usluga", back_populates="termini")

class Recenzija(Base):
    __tablename__ = "recenzije"
    id = Column(Integer, primary_key=True, index=True)
    ocjena = Column(Integer, nullable=False)
    komentar = Column(Text, nullable=True)
    korisnik_id = Column(Integer, ForeignKey("korisnici.id"), nullable=False)
    frizer_id = Column(Integer, ForeignKey("frizeri.id"), nullable=False)

    korisnik = relationship("Korisnik", back_populates="recenzije")
    frizer = relationship("Frizer", back_populates="recenzije")
