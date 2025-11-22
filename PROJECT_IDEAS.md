# 🚀 Project Ideas (Short Version)

Drie compacte projectconcepten voor het Webtechnologie-1 project.  
Alle projecten gebruiken **Flask + SQLite + Bootstrap**, met gesimuleerde **Web3-mechanieken** zoals hashing, blocks en time-locks.

---

## 1. EncryptedTimeCapsule  
**Veilige digitale capsules die pas na een ingestelde datum geopend kunnen worden.**

### Concept  
Gebruikers maken een persoonlijke “time capsule” die één of meerdere elementen bevat:  
- een tekstbericht  
- een afbeelding/foto  
- een optioneel extra bestand (bijv. video, pdf, audio)  

Alles wordt AES-encrypted opgeslagen.  
Bij het aanmaken kiest de gebruiker een unlock-datum of -tijd.  
Wanneer deze datum bereikt is, wordt de gebruiker én opgegeven contacten automatisch genotificeerd.

### Kernfeatures  
- Meerdere inhoudstypes: tekst + afbeelding + extra bestand  
- AES-encryptie van alle capsule-onderdelen  
- Unlock timer + countdown  
- E-mailnotificatie bij unlock  
- SMS/telefoonnummer-notificatie (gesimuleerd via backend logica)  
- SHA-256 hash per capsule voor integrity  
- Logboek van alle acties  
- **Leuke extra:** “Surprise Mode”  
  - content blijft verborgen (geen preview) tot de unlock-datum  
  - capsule toont alleen een animatie / teaser
---

## 2. GiftChain + ProofOfCreator  
**Digitale gifts en creator-assets vastgelegd als blocks in een pseudo-blockchain.**

### Concept  
Gebruikers kunnen:  
- digitale gifts sturen (tekst, tokens, kleine bestanden), en  
- eigen content uploaden als “creator asset”.  

Elke actie wordt een block met hash + previous_hash, wat een onveranderbare chain vormt.  
Creators krijgen automatisch een ownership hash over hun content.

### Kernfeatures  
- Gifts versturen/ontvangen  
- Creator assets uploaden (video/beeld/document)  
- SHA-256 hashing per asset  
- Blockstructuur: hash, previous_hash, timestamp  
- Chain explorer + integrity checker  
- Dashboard met gift- en ownership-geschiedenis

---

## 3. Web3 Proof-of-Attendance  
**Event-badges die fungeren als verifieerbare deelnamebewijzen.**

### Concept  
Gebruikers kunnen een event “joinen” (bijv. met een QR of code).  
Bij deelname krijgen ze een **attendance badge** met hash, zoals een POAP, maar volledig zonder echte blockchain.

### Kernfeatures  
- Event registreren/joinen  
- Unieke hashed attendance badge  
- Badge gallery per gebruiker  
- Verify endpoint: `/badge/<hash>`  
- Timeline met alle bezochte events

---

