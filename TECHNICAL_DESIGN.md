# 🧩 TECHNICAL_DESIGN – GiftChain + ProofOfCreator(InstaChain)

Een technisch ontwerp voor de Web3-geïnspireerde webapplicatie **GiftChain + ProofOfCreator**.  
De app gebruikt **Flask + SQLite + Bootstrap** en simuleert Web3-mechanieken zoals hashes, blocks, immutability en chain-integrity.

---

## 1. 🎯 Conceptueel Overzicht

De applicatie combineert twee hoofdconcepten:

### 1.1 ProofOfCreator
Gebruikers (creators) uploaden bestanden (afbeeldingen, video’s, documenten, etc.).  
Voor elk bestand wordt een **SHA-256 hash** berekend. Deze hash wordt:

- gekoppeld aan de ingelogde gebruiker (eigenaar)
- opgeslagen in de database
- opgenomen als block in een pseudo-blockchain (`ChainBlock`)

Dit fungeert als een ownership proof (NFT-achtig, maar off-chain).

### 1.2 GiftChain
Gebruikers kunnen **digitale gifts** naar elkaar sturen, bestaande uit:

- tekstbericht  
- optioneel een “token amount” (bijv. 10 tokens, gesimuleerd)  
- optioneel een attachment (klein bestand)

Elke gift wordt ook vastgelegd in de chain als `ChainBlock` met:

- hash  
- previous_hash  
- timestamp  
- payload (gift data)

De combinatie van alle blocks vormt een **onveranderbare event-chain**: uploads + gifts.

---

## 2. 🏛 High-level Architectuur

### Frontend
- HTML-templates met **Jinja2** in `templates/`
- UI-styling met **Bootstrap 5**
- Formulieren voor:
  - login/registratie
  - bestanden uploaden (ProofOfCreator)
  - gifts versturen (GiftChain)
- Pagina’s:
  - dashboard
  - gift-overzichten
  - creator assets
  - chain explorer
  - integrity check
  - ownership proof pagina (`/asset/<id>`)

### Backend (Flask)
- Routing & controllers in:
  - `routes.py` (dashboard, gifts, chain, creator)
  - `auth.py` (login, register, logout)
- Businesslogica voor:
  - gifts
  - file uploads
  - creator assets
- Chain- en hash-logica in:
  - `chain_utils.py`
- Configuratie / app-factory in:
  - `__init__.py`

### Database (SQLite + SQLAlchemy)
- Persistent databasebestand `instance/app.db`
- ORM-modellen:
  - `User`
  - `CreatorAsset`
  - `Gift`
  - `ChainBlock`

### Filesystem
- `uploads/creator_assets/` – bestanden van ProofOfCreator
- `uploads/gifts/` – attachments van gifts
- `instance/app.db` – SQLite database

---

## 3. 🗄 Data Model (Database)

### 3.1 User

```text
User
- id (PK, int)
- username (string, unique)
- email (string, unique)
- password_hash (string)
- created_at (datetime)
```
### 3.2 CreatorAsset (ProofOfCreator)
```text
CreatorAsset
- id (PK, int)
- user_id (FK → User.id)
- original_filename (string)
- stored_filename (string)        # naam op de server (bijv. UUID)
- file_hash (string)              # SHA-256 hash
- file_type (string)              # image/video/document/pdf/etc.
- created_at (datetime)
```
### 3.3 Gift (GiftChain)
```text
Gift
- id (PK, int)
- sender_id (FK → User.id)
- receiver_id (FK → User.id)
- message (text)
- token_amount (int, nullable)          # optioneel, bijv. 10 tokens
- attachment_filename (string, nullable)
- created_at (datetime)
```
### 3.4 ChainBlock (pseudo-blockchain)
```text
ChainBlock
- id (PK, int, auto-increment)
- block_type (string)            # "gift" | "creator_asset"
- ref_id (int)                   # verwijzing naar Gift.id of CreatorAsset.id
- hash (string)                  # SHA-256(payload_json + previous_hash)
- previous_hash (string)         # hash van vorig block, of "0" bij eerste block
- payload_json (text)            # snapshot van relevante data in JSON
- created_at (datetime)
```
Ontwerpkeuze:
De “echte” data staat in Gift en CreatorAsset.
De ChainBlock is een append-only eventlog voor immutability.


# 4. 🔐 Chain / “Smart Contract” Logica (Simulatie)

Chain-logica wordt geïmplementeerd in Python, bijvoorbeeld in chain_utils.py.

### 4.1 Block creatie (pseudo-smart-contract)
```python
import json
from hashlib import sha256
from datetime import datetime
from app.models import ChainBlock, db

def create_block(block_type: str, ref_id: int, payload: dict) -> ChainBlock:
    # Haal laatste block op
    previous_block = ChainBlock.query.order_by(ChainBlock.id.desc()).first()
    previous_hash = previous_block.hash if previous_block else "0"

    # Payload deterministisch serialiseren
    payload_str = json.dumps(payload, sort_keys=True)

    # Hash berekenen: payload + previous_hash
    raw = payload_str + previous_hash
    new_hash = sha256(raw.encode("utf-8")).hexdigest()

    # Nieuw block opslaan
    block = ChainBlock(
        block_type=block_type,
        ref_id=ref_id,
        payload_json=payload_str,
        previous_hash=previous_hash,
        hash=new_hash,
        created_at=datetime.utcnow()
    )

    db.session.add(block)
    db.session.commit()
    return block
```

### 4.2 Chain Integrity Check

Route: /chain/integrity
Doel: controleren of de chain niet corrupt is.

Pseudocode:
```python
def verify_chain_integrity():
    blocks = ChainBlock.query.order_by(ChainBlock.id.asc()).all()
    previous_hash = "0"
    errors = []

    for block in blocks:
        # Herbereken hash
        raw = block.payload_json + previous_hash
        recalculated_hash = sha256(raw.encode("utf-8")).hexdigest()

        # Vergelijk met opgeslagen hash
        if recalculated_hash != block.hash:
            errors.append(f"Hash mismatch bij block {block.id}")

        # Check previous_hash-consistentie
        if block.previous_hash != previous_hash:
            errors.append(f"Previous hash mismatch bij block {block.id}")

        # Prepare next
        previous_hash = block.hash

    return errors  # leeg = chain is geldig
```
# 5. 👤 Belangrijkste User Flows

## 5.1 Flow: ProofOfCreator (Asset Upload)

1. Gebruiker logt in.  
2. Navigeert naar `/creator/upload`.  
3. Uploadt een bestand (en optioneel extra info).  
4. Backend:
   - slaat bestand op in `uploads/creator_assets/`
   - berekent SHA-256 hash van het bestand
   - maakt een `CreatorAsset` record aan
   - bouwt payload (bijv. `{ "user_id": X, "file_hash": "...", "filename": "..." }`)
   - roept `create_block("creator_asset", asset.id, payload)` aan  
5. Gebruiker wordt doorgestuurd naar `/creator/assets`.  
6. Elke asset heeft een detailpagina (`/creator/asset/<id>`) met de ownership proof.

---

## 5.2 Flow: Gift versturen (GiftChain)

1. Ingelogde gebruiker gaat naar `/gifts/send`.  
2. Formuliervelden:
   - ontvanger (dropdown met users)
   - bericht (tekst)
   - optioneel `token_amount`
   - optioneel attachment  
3. Backend:
   - slaat attachment op in `uploads/gifts/` (indien aanwezig)
   - maakt `Gift` record
   - stelt payload samen (sender, receiver, tokens, message, timestamps)
   - roept `create_block("gift", gift.id, payload)` aan  
4. Gebruiker ziet de gift terug in:
   - `/gifts/sent`
   - `/gifts/received` (bij de ontvanger)
   - `/chain` (als block)

---

## 5.3 Flow: Chain Explorer

- Route: `/chain`  
- Haalt alle `ChainBlock` records op (orde: `id ASC`).  
- Toont per block:
  - `id`
  - `block_type` (gift / creator_asset)
  - korte payloadsamenvatting (bijv. “Gift van A naar B”, “Asset van C”)
  - ingekorte `hash` en `previous_hash`
  - link naar onderliggend object (`Gift` of `CreatorAsset`)

---

## 5.4 Flow: Hash Verification

- Route: `/verify/<hash>`  
- Controleert of:
  - `CreatorAsset.file_hash == hash`, of  
  - `ChainBlock.hash == hash`  
- Toont:
  - of de hash bekend is  
  - bij welke asset/gift/block deze hoort  
  - eigenaar (bij assets)  
  - timestamp en payloadinfo  

---

# 6. 🎨 Front-end Ontwerp & Design Keuzes

## 6.1 UI Framework

- **Bootstrap 5** voor layout, grid, buttons en forms.  
- Consistente kleurstelling (eventueel Web3/Polkadot-stijl):
  - donkere achtergrond  
  - paarse en turquoise accenten  
  - cards met subtiele shadows  

---

## 6.2 Belangrijke Templates

| Template | Omschrijving |
|---------|--------------|
| `base.html` | Basislayout, navbar, footer |
| `index.html` | Landing page met uitleg |
| `auth/login.html`, `auth/register.html` | Authenticatie |
| `dashboard.html` | Samenvatting: aantal assets/gifts, laatste blocks |
| `creator/assets.html` | Lijst met geüploade assets |
| `creator/asset_upload.html` | Uploadpagina |
| `creator/asset_detail.html` | Ownership proof view |
| `gifts/send.html` | Gift versturen |
| `gifts/list_sent.html` | Verstuurde gifts |
| `gifts/list_received.html` | Ontvangen gifts |
| `chain/index.html` | Chain explorer |
| `chain/integrity.html` | Resultaat chain integrity check |

---

## 6.3 UX Richtlijnen

- Duidelijke navigatiecategorieën:
  - **Dashboard**
  - **Creator Assets**
  - **Gifts**
  - **Chain**
- Iconen:
  - 🎁 → gifts  
  - 🧩 → blocks  
  - 🎨 / 📁 → assets  
- Korte toelichtingsteksten op chain- en proof-pagina’s, zodat non-tech gebruikers begrijp wat ze zien.

---

# 7. 🔒 Security & Validatie

## Password Security
- Hashing via `werkzeug.security.generate_password_hash`
- Verificatie via `check_password_hash`

## File Uploads
- Alleen whitelisted extensies toegestaan
- Maximale bestandsgrootte via Flask-config
- Bestandsnamen vervangen door UUID’s

## CSRF-bescherming
- Gebruik van Flask-WTF formulieren

## Input Validatie
- Server-side controle (formulierwaarden, verplichte velden)

## Chain Immutability
- `ChainBlock` records worden **nooit geüpdatet**, alleen toegevoegd  
- Bronrecords kunnen optioneel soft-deleted worden, maar blocks blijven bestaan

---

# 8. 📁 Projectstructuur

```text
project_root/
│
├── app/
│   ├── __init__.py          # app factory, db-init
│   ├── models.py            # User, CreatorAsset, Gift, ChainBlock
│   ├── routes.py            # dashboard, gifts, creator, chain
│   ├── auth.py              # login, register, logout
│   ├── chain_utils.py       # hashing, block-creation, integrity checks
│   ├── static/              # css, js, images
│   └── templates/           # HTML (Jinja2)
│
├── uploads/
│   ├── creator_assets/
│   └── gifts/
│
├── instance/
│   └── app.db               # SQLite database
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── ROADMAP.md
└── TECHNICAL_DESIGN.md
```
# 9. 💡 Design Keuzes – Samenvatting

### ✔ Flask + SQLite  
Lichtgewicht, makkelijk te deployen, cross-platform en perfect passend binnen de vereisten van **Webtechnologie 1**.

---

### ✔ Pseudo-blockchain (ChainBlock)

- **append-only** data-structuur  
- elk block bevat:  
  - `hash`  
  - `previous_hash`  
- vormt een eenvoudige maar effectieve simulatie van blockchain-immutability  
- goed uitlegbaar tijdens criteriumgesprek en technisch helder

---

### ✔ SHA-256 Hashing  
- Gebruik van industriestandaard hashing  
- Beschikbaar via Python's `hashlib`  
- Biedt betrouwbaarheid, consistentie en transparantie  
- Toegepast op bestanden, gifts en block payloads  

---

### ✔ Duidelijke Scheiding van Verantwoordelijkheden (SoC)

| Onderdeel | Bestand | Verantwoordelijkheid |
|----------|----------|----------------------|
| **ORM / Database logica** | `models.py` | SQLAlchemy-modellen (User, CreatorAsset, Gift, ChainBlock) |
| **Chain & hashing logica** | `chain_utils.py` | block-creatie, hashing, integrity-checks |
| **Routing / Business controllers** | `routes.py`, `auth.py` | dashboard, gifts, uploads, chainpagina’s, login/register |
| **Frontend & UI** | `templates/`, `static/` | HTML, Jinja2, Bootstrap styling |

Deze structuur zorgt voor:
- onderhoudbaarheid  
- uitbreidbaarheid  
- overzichtelijkheid voor docenten en reviewers  

---

### ✔ Eenvoudige & Toegankelijke Frontend

Frontend wordt bewust simpel gehouden zodat de focus ligt op:

- **hashing** (begrijpen hoe datafingerprints werken)
- **chainstructuren** (block-types, linking, immutability)
- **ownership proofs** (creator content → bewijs van eigendom)

Met behulp van Bootstrap voor:
- responsieve paginastructuur  
- overzichtelijke kaarten (cards)  
- duidelijke navigatie  
- goed leesbare chain explorer  

---

**Samengevat:**  
Dit ontwerp is modern, helder, technisch verantwoord, en volledig passend binnen de scope van de opleiding—met een Web3 twist die het project onderscheidend en innovatief maakt.

