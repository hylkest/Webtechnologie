# 🚀 Project Ideas – Webtechnologie 1

In dit document staan verschillende projectideeën die aansluiten bij de eisen van de module **Webtechnologie 1** (HTML/CSS/Bootstrap + Flask + SQLite + SQLAlchemy).  
Daarnaast bevatten de concepten lichte Web3-elementen (gesimuleerd), zonder dat er echte blockchain-integraties nodig zijn.

---

## 📌 Project 1 — ContentProof  
**Digitale eigendomsregistratie voor video’s via hash-verificatie**

### 🎯 Concept
Content creators kunnen een video uploaden (MP4, MOV, etc.).  
Het systeem genereert automatisch een **SHA-256 hash** van het bestand en koppelt deze aan het account van de gebruiker.  
Deze hash fungeert als een “ownership proof”, vergelijkbaar met een NFT maar volledig **gesimuleerd** binnen Flask.

### 🔧 Belangrijkste functies
- Uploaden van video’s via een bootstrap-formulier  
- Automatische SHA-256 hashing  
- Registratie in de SQLite-database  
- Dashboard met alle gehashte video's  
- “Eigendomssimulatie” via user accounts  
- Optioneel: een mini-blockchain (hash + previous hash)  

### 📁 Voorbeeld database tabellen
- `users`  
- `videos`  
- `video_hashes` (hash, timestamp, user_id)

---

## 📌 Project 2 — CryptoTikkie  
**Crypto-giftcards met locked tokens (Web3 gift simulator)**

### 🎯 Concept
Gebruikers kunnen een digitaal cadeau sturen (bijvoorbeeld 10 “tokens”).  
Deze tokens worden **gelocked** voor een bepaald aantal maanden of jaren.  
Pas wanneer de unlock-datum bereikt is, kan de ontvanger de tokens claimen.

Dit simuleert het gedrag van een smart contract.

### 🔧 Belangrijkste functies
- Dashboard met saldo  
- Tokens versturen naar andere gebruikers  
- Locking rules via Python/Flask  
- Unlock countdown op de frontend  
- Transactiegeschiedenis via SQLite  
- Views voor:  
  - verstuurde gifts  
  - ontvangen gifts  
  - tokens claimen  

### 📁 Voorbeeld database tabellen
- `users`  
- `wallets`  
- `locked_gifts`  
- `transactions`

---

## 💡 Waarom deze ideeën geschikt zijn
- Sluiten 100% aan op de module-eisen  
- Gebruiken HTML + Bootstrap  
- Gebruiken Flask views en formulieren  
- Gebruiken SQLite/SQLAlchemy  
- Simuleren smart contract logica zonder externe libraries  
- Zijn origineel, creatief en goed verdedigbaar tijdens een criteriumgericht interview  

---

## 📌 Aanvullende ideeën
- Leaderboard voor creators met meest gehashte content  
- “Gift gallery” voor CryptoTikkie met mooie UI  
- Mini-blockchain: elke actie is een “block” met timestamp  
- API endpoint `/verify/<hash>` om eigendom te valideren  

---

## 📝 Status
- [ ] Idee gekozen  
- [ ] Basisstructuur Flask klaar  
- [ ] Database ontwerp  
- [ ] MVP routes  
- [ ] UI ontwerp  
- [ ] Eindpresentatie voorbereiden  

---

## ✨ Auteur
Levano Moermond  
Webtechnologie 1 – Projectconcepten  

