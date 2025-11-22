# 🗺️ Project Roadmap

Dit document beschrijft de volledige ontwikkelroute van het project, opgedeeld in logische fases.  
We beginnen met lokale app-ontwikkeling (HTML + Flask), daarna de database, vervolgens de smart-contract-simulatie, en eindigen met containerization en deployment.

---

# 1. 🚧 Fase 1 — Basis App Development (Lokaal)

Doel: Een minimale werkende Flask-app met HTML-templates en basisrouting.

### Taken
- [ ] Projectstructuur opzetten (`app/`, `templates/`, `static/`)
- [ ] Flask installeren & basis-app aanmaken
- [ ] Startpagina + layout met Bootstrap
- [ ] User authenticatie (registreren, inloggen, uitloggen)
- [ ] Basis navigatie: dashboard, upload, chain, gifts
- [ ] Lokale file uploads testen (geen hashing nog)

### Deliverables
- Werkende Flask-app
- HTML-layout + basis styling
- Users kunnen inloggen en files uploaden

---

# 2. 🗄️ Fase 2 — Database Layer (SQLite + SQLAlchemy)

Doel: Alle core models maken en de database persistent krijgen.

### Taken
- [ ] Database aanmaken (`instance/app.db`)
- [ ] SQLAlchemy models implementeren:
  - `User`
  - `CreatorAsset`
  - `ChainBlock`
- [ ] Database migraties (creëren + initialiseren)
- [ ] CRUD voor uploads en gifts
- [ ] Relaties testen (user → assets → blocks)

### Deliverables
- SQLite database actief
- Alle modellen werkend en opslaan/uitlezen getest

---

# 3. 🔐 Fase 3 — Smart Contract-Simulatie (Hashing + Blocks)

Doel: De core blockchain-achtige functionaliteit realiseren.

### Taken
- [ ] SHA-256 hashing implementeren voor:
  - Creator assets
  - Gifts
- [ ] `create_block()` functie bouwen
- [ ] Previous hash → block chain linking
- [ ] Chain explorer (`/chain`)
- [ ] Integrity checker (`/integrity`)
- [ ] Ownership verify endpoint: `/verify/<hash>`

### Deliverables
- Volledige pseudo-blockchain
- Assets & gifts vastgelegd als immutable blocks
- Chain explorer werkt

---

# 4. 🎁 Fase 4 — GiftChain Functionaliteit

Doel: Gifts versturen & ontvangen implementeren.

### Taken
- [ ] Gifts versturen formulier
- [ ] Optie voor tekst, tokens, afbeelding, mini-file
- [ ] Opslaan in database
- [ ] Block genereren met gift payload
- [ ] Dashboard:
  - verstuurde gifts
  - ontvangen gifts

### Deliverables
- Gifts werken end-to-end
- Gifts verschijnen in de chain

---

# 5. 🎨 Fase 5 — ProofOfCreator Functionaliteit

Doel: Creator-content uploaden en ownership hashes genereren.

### Taken
- [ ] File upload + hash genereren
- [ ] Asset record aanmaken + block entry
- [ ] Creator dashboard maken
- [ ] `/asset/<id>` pagina voor ownership proof
- [ ] File preview of meta-card

### Deliverables
- Creator proof systeem volledig werkend
- Assets verschijnen in chain en zijn verifieerbaar

---

# 6. 🧪 Fase 6 — Polishing & Testing

Doel: App gebruiksklaar maken.

### Taken
- [ ] Frontend polishing (Bootstrap UI)
- [ ] Validatie formulieren (Flask-WTF)
- [ ] Unit tests voor block hashing
- [ ] File size limits & veilige uploads
- [ ] Error handling (404, 500, invalid hash)

### Deliverables
- Stabiele lokale applicatie
- Volledige functionaliteit bevestigd

---

# 7. 🐳 Fase 7 — Containerization (Docker)

Doel: App volledig containerized krijgen.

### Taken
- [ ] `Dockerfile` maken (Python 3.12)
- [ ] `docker-compose.yml` maken voor lokale volumes
- [ ] Volume toevoegen voor:
  - uploads
  - SQLite database
- [ ] Environment variables via `.env`
- [ ] Testen via:  
  ```bash
  docker compose up --build
