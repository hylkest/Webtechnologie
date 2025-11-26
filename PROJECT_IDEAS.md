# Proof of Concept – InstChain (Instagram Clone + Hashchain + Rewards)

## Doel
Aantonen dat een minimale versie van het systeem werkbaar is:
- Users kunnen registreren en inloggen.
- Afbeeldingen kunnen worden geüpload en weergegeven in een feed.
- Elke upload wordt gehasht en toegevoegd aan een eenvoudige blockchain.
- Users kunnen elkaar belonen met credits.

## Minimale functionaliteit (MVP)
### 1. Authenticatie
- Registreren met username + wachtwoord.
- Inloggen via Flask session.
- Password hashing via Werkzeug.

### 2. Post Upload
- Enkele afbeelding uploaden.
- Opslag in `/static/uploads/`.
- Post wordt zichtbaar in de feed.

### 3. Hashchain
- Elke nieuwe post genereert een SHA-256 hash.
- Hash wordt aan een `Block` gekoppeld.
- Block bevat: `post_id`, `hash`, `previous_hash`, timestamp.
- Chain wordt opgeslagen in SQLite.

### 4. Reward System
- Elke user heeft een balance (default 100 credits).
- Onder een post kan een reward worden gestuurd.
- Saldi worden automatisch bijgewerkt.
- Transactie wordt opgeslagen.

## Verwachte Output
- Werkende route `/upload` + feed.
- Werkende hash-chain zichtbaar via `/chain`.
- Functionerend reward-systeem met balansen.

## Resultaat POC
De eerste versie valideert alle kerntechnieken:
- Flask werkt en render templates.
- Databaseverbinding met SQLAlchemy functioneert.
- Uploads worden correct verwerkt.
- Hashchain genereert correcte hashes.
- Rewards voeren balansmutaties correct uit.

POC geslaagd → project kan volledig worden ontwikkeld.
