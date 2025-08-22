# frizerski-salon-fastapi 

Backend aplikacija za upravljanje rezervacijama u frizerskom salonu.  
Korištene tehnologije: **Python**, **FastAPI**, **SQLAlchemy**, **MySQL**, **Redis** i **Docker**.

---

## Funkcionalnosti

### Korisnici
- Registracija i login korisnika
- CRUD operacije za korisnike
- Sigurna pohrana lozinki (hashirane)

### Frizeri
- CRUD operacije za frizere
- Prosječna ocjena frizera
- Brisanje frizera automatski briše njegove termine i recenzije (kaskadno)

### Usluge
- CRUD operacije za usluge 

### Termini
- CRUD operacije za termine
- Povezivanje termina s korisnikom, frizerom i uslugom

### Recenzije
- CRUD operacije za recenzije
- Povezivanje recenzija s korisnikom i frizerom

---

Pokretanje: docker-compose up --build

API će biti dostupan na: http://localhost:8000

