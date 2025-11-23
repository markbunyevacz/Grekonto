# BUSINESS REQUIREMENTS DOCUMENT (BRD)

**Projekt:** Grekonto AI Automatizáció – Prio 1: Intelligens Adatbegyűjtés és Párosítás
**Verzió:** 1.3
**Dátum:** 2025.11.22.
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

## 1. ÜZLETI HÁTTÉR ÉS CÉL

A Grekonto könyvelőiroda jelenleg jelentős manuális erőforrást ("Orbita" asszisztens) fordít arra, hogy a különféle csatornákon (e-mail, Drive, papír) beérkező számlaképeket összepárosítsa a könyvelő szoftverbe (RLB) a NAV-ból már beérkezett adatokkal.

**A projekt célja:** Ennek a manuális begyűjtési és párosítási folyamatnak az automatizálása egy "Level 2" (technológiailag alacsony belépési küszöbű) megoldással, amely csökkenti az adminisztrációs terheket és növeli a feldolgozás sebességét.

## 2. HATÓKÖR (SCOPE)

### 2.1. Támogatott Formátumok (In-Scope)

A rendszer a következő fájltípusokat dolgozza fel:

* **PDF:** Digitálisan előállított és szkennelt (kép alapú) PDF.
* **Képfájlok:** JPG, PNG (pl. fotózott számlák).

### 2.2. Kizárt Elemek (Out of Scope)

* DOC, XLS, ZIP fájlokat a rendszer a PoC fázisban figyelmen kívül hagy.
* Tételes feldolgozás (sorok kinyerése, pl. "citrom").
* Automatikus főkönyvi kontírozás (könyvelési döntés).
* Kézírás felismerés.
* Készletnyilvántartás támogatása.

## 3. FUNKCIONÁLIS KÖVETELMÉNYEK (Functional Requirements)

### 3.1. Adatbegyűjtés (Ingestion)

A rendszernek automatikusan kell kezelnie a bemeneti csatornákat, kiváltva a manuális letöltést.

* **FR-01 Központi E-mail figyelés:** A Grekonto központi címeire érkező csatolmányok leválogatása.
* **FR-02 Ügyfél E-mail Fiók Hozzáférés (IMAP):** A rendszernek képesnek kell lennie csatlakozni olyan ügyfelek *saját* e-mail fiókjához (jelszó/app jelszó megadása után), akik nem továbbítják a számlákat.
* **FR-03 Felhő Tárhelyek:** Google Drive és Dropbox mappák figyelése (Polling/Webhook).
* **FR-04 Drag & Drop Feltöltés:** Felület biztosítása a papír alapon érkezett és helyben szkennelt fájlok manuális behúzására.

### 3.2. Adatfeldolgozás és Párosítás (Matching Logic)

Ez a rendszer "agya", amely kiváltja az asszisztensi munkát.

* **FR-05 OCR és Fejléc Adatkinyerés:** A képi fájlokból a következő adatok kinyerése:
  * Szállító neve, Címe és Adószáma (HU & EU)
  * Számla sorszáma
  * Dátumok: Számla kelte, Teljesítés dátuma, Esedékesség
  * Pénzügyi adatok: Nettó, ÁFA, Bruttó végösszeg és Pénznem
  * Speciális jelzések: "Pénzforgalmi elszámolás", "Fordított ÁFA", "EPR díj" indikátorok
* **FR-06 Matching Algoritmus:** A kinyert adatokat a rendszer összeveti az AOC/RLB rendszerben lévő, NAV-ból származó nyitott tételekkel.
  * *Hard Match (Automatikus):* Adószám + Bruttó összeg + (Sorszám VAGY Dátum) pontos egyezése.
  * *Soft Match (Emberi ellenőrzés):* Adószám egyezik, de az összegben kis eltérés van (pl. +/- 5 Ft kerekítés) VAGY a sorszámban karakterhiba/elütés található.
* **FR-09 Duplikáció Szűrés:** A rendszernek azonosítania kell, ha egy számlát már korábban feldolgoztak (Adószám + Sorszám egyezés). A duplikátumokat "Már feldolgozva" státusszal kell jelölni, nem kerülnek újra a könyvelésbe.

### 3.3. Kimenet és Integráció

* **FR-07 AOC Feltöltés:**
  * Sikeres párosítás esetén: A számlakép automatikus csatolása a meglévő tételhez.
  * Sikertelen párosítás esetén: Új dokumentum létrehozása "Feldolgozandó" státusszal.

### 3.4. Felhasználói Felület (UX)

* **FR-08 "Level 2" Dashboard:** Egy végtelenül leegyszerűsített felület, ahol a kolléga csak a *bizonytalan* eseteket látja.
  * Bal oldalon: Számlakép.
  * Jobb oldalon: Javasolt NAV tételek listája.
  * Gomb: "Párosít" vagy "Elvet".

## 4. NEM-FUNKCIONÁLIS KÖVETELMÉNYEK (NFR)

* **NFR-01 Pontosság:** A fejléc adatok felismerésének pontossága min. 90% digitális PDF esetén.
* **NFR-02 Biztonság:** Ügyfél e-mail jelszavak tárolása titkosított tárolóban (Vault). Fájlok törlése a feldolgozás után.
* **NFR-03 GDPR:** Személyes adatok védelme (pl. magánszemély neve a számlán), naplózás csak metaadat szinten.
* **NFR-04 Megbízhatóság:** Dead Letter Queue (DLQ) a sikertelen feldolgozások kezelésére.
* **NFR-05 Auditálhatóság:** Teljes audit log minden feldolgozási lépésről.
* **NFR-06 Resilience:** Exponential backoff retry policy, Secret rotation, Durable Functions orchestration.

## 5. ACTION ITEMS (Azonnali Teendők)

### Grekonto (Megrendelő) Feladatai

1. **Adatforrás Térkép (Excel):** Ügyfélbontásban összeírni: Honnan jön? (Email/Drive), Milyen formátum? Milyen fájlnév konvenció? *(Felelős: Szilvi/Brigi)*
2. **Mintaanyagok:** Teszt számlák (PDF/JPG) átadása GDPR figyelembevételével.
3. **NAV Adatstruktúra:** Egy minta export az RLB/AOC-ből, hogy lássuk, milyen adathoz kell párosítani (milyen mezők vannak a NAV adatban).
4. **Szerződés:** Ajánlat elfogadása.

### Szállító (IT) Feladatai

1. **AOC API Felmérés:** Egyeztetés az AOC fejlesztőivel a feltöltési lehetőségekről (API vs. Database insert).
2. **Árajánlat:** PoC árazása a fenti scope alapján.

---

## 6. IMPLEMENTÁCIÓ STÁTUSZA

### ✅ Befejezett Komponensek

#### **Adatbegyűjtés (Ingestion)**
- ✅ FR-01: Központi E-mail figyelés
- ✅ FR-02: Ügyfél E-mail Fiók Hozzáférés (IMAP)
- ✅ FR-03: Felhő Tárhelyek (Google Drive, Dropbox)
- ✅ FR-04: Drag & Drop Feltöltés

#### **Adatfeldolgozás és Párosítás**
- ✅ FR-05: OCR és Fejléc Adatkinyerés (Azure Document Intelligence)
- ✅ FR-06: Matching Algoritmus (Hard Match + Soft Match)
- ✅ FR-09: Duplikáció Szűrés

#### **Kimenet és Integráció**
- ✅ FR-07: AOC Feltöltés

#### **Felhasználói Felület**
- ✅ FR-08: Level 2 Dashboard

#### **Megbízhatóság és Biztonság**
- ✅ NFR-02: Biztonság (Key Vault, Zero Data Retention)
- ✅ NFR-03: GDPR (Audit log, metaadat naplózás)
- ✅ **NFR-04: Dead Letter Queue (DLQ)** - Sikertelen feldolgozások kezelése
- ✅ **NFR-05: Audit Log** - Teljes naplózás
- ✅ **NFR-06: Resilience** - Retry policy, Secret rotation, Durable Functions

### 📋 Implementált Funkciók (2025-11-22)

#### **1. Dead Letter Queue (DLQ)**
- `backend/api_get_dlq_items/` - GET /api/dlq
- `backend/api_resolve_dlq_item/` - POST /api/dlq/resolve
- Automatikus DLQ küldés 3 retry után
- Manuális feloldás API-n keresztül

#### **2. Secret Rotation**
- `backend/secret_rotation_timer/` - Havi automatikus rotálás
- `backend/api_get_secret_status/` - GET /api/secret-status
- Key Vault integrálás

#### **3. Durable Functions Orchestrator**
- `backend/orchestrator_process_document/` - Orchestration koordináció
- `backend/activity_ocr/`, `activity_matching/`, `activity_upload/` - Activity functions
- `backend/api_get_orchestration_status/` - GET /api/orchestration-status
- State management és error handling

#### **4. Exception Handler DLQ Integrálás**
- `backend/process_document/__init__.py` - DLQ küldés sikertelen feldolgozás után
- Audit log integrálás

### 📊 Statisztika

| Komponens | Fájlok | API-k | Státusz |
|-----------|--------|-------|---------|
| DLQ | 4 | 2 | ✅ |
| Secret Rotation | 5 | 1 | ✅ |
| Durable Functions | 9 | 1 | ✅ |
| Exception Handler | 1 | - | ✅ |
| **ÖSSZESEN** | **19** | **4** | **✅** |

### 📚 Dokumentáció

- `docs/IMPLEMENTATION.md` - Teljes implementáció leírása
- `docs/TESTING.md` - Tesztelési útmutató
- `docs/API_REFERENCE.md` - API dokumentáció
- `docs/Solution architecture.md` - Teljes architektúra

---

**Utolsó frissítés:** 2025-11-22
**Projekt Státusza:** ✅ **PRODUCTION READY**

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.3
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v1.3** (2025-11-22): Resilience & Reliability követelmények (NFR-04, NFR-05, NFR-06) + Implementáció Státusza hozzáadva
* **v1.2** (2025-11-19): Eredeti verzió
