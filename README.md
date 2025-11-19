# Grekonto AI Automatizáció

Ez a projekt a Grekonto könyvelőiroda számára készült AI alapú automatizációs rendszer (PoC), amelynek célja a számlafeldolgozás és párosítás automatizálása.

## Projekt Struktúra

- **backend/**: Azure Functions (Python) alapú backend szolgáltatások.
  - `ingestion/`: Adatbegyűjtő funkciók (Email, Drive, Dropbox).
  - `processing/`: Feldolgozó és párosító logika (OCR, Matching Engine).
  - `shared/`: Közös kódkészlet (Adatbázis modellek, segédfüggvények).
- **frontend/**: React alapú felhasználói felület (Level 2 Dashboard).
- **infrastructure/**: Azure erőforrás leírók (IaC).
- **docs/**: Projekt dokumentáció (BRD, Architektúra, UX tervek).

## Dokumentáció

A részletes dokumentáció a `docs/` mappában található:

- [Üzleti Követelmények (BRD)](docs/BRD.md)
- [Megoldás Architektúra](docs/Solution%20architecture.md)
- [Felhasználói Élmény (UX)](docs/User%20Experience.md)

## Fejlesztés

### Előfeltételek

- Python 3.9+
- Node.js 18+
- Azure Functions Core Tools
- Azure CLI

### Indítás

(Részletes instrukciók hamarosan...)
# Grekonto
