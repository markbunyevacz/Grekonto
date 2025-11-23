# SENIOR SOLUTION ARCHITECTURE DOCUMENT (SAD)

**Projekt:** Grekonto AI – Prio 1 (Smart Matching & Ingestion)
**Verzió:** 2.1
**Dátum:** 2025-11-22
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)
**Készítette:** Senior System Architect

## 1. RENDSZERDIAGRAM (High-Level Architecture)

A rendszer az **Azure Cloud** környezetben fut, Event-Driven (eseményvezérelt) elven.

```mermaid
graph TD
    subgraph "1. INGESTION LAYER (Begyűjtés)"
        E_CENTRAL[Központi Grekonto E-mailek] -->|Auto-Forward / Graph API| INGEST_FUNC[Azure Function: Ingestion Service]
        E_CLIENT[Ügyfél E-mail Fiókok\n(IMAP)] -->|Secure Poll| INGEST_FUNC
        G_DRIVE[Google Drive / Dropbox] -->|Webhook / Poll| INGEST_FUNC
        MANUAL[Drag & Drop UI] -->|Upload| INGEST_FUNC
        
        KEY_VAULT[Azure Key Vault\n(Ügyfél Jelszavak & API Kulcsok)] -.->|Credentials| INGEST_FUNC
    end

    subgraph "2. CORE PROCESSING (Feldolgozás)"
        INGEST_FUNC -->|1. Fájl Validáció\n(PDF/JPG only, NO DOCX)| STORAGE_RAW[Blob Storage\n(Raw Files)]
        STORAGE_RAW -->|2. Trigger| ORCHESTRATOR[Durable Functions\n(Orchestrator)]
        
        ORCHESTRATOR -->|3. OCR & Header Extraction| AI_DOC[Azure Document Intelligence\n(Pre-built Invoice Model)]
        AI_DOC -->|4. JSON Data| MATCH_ENGINE[Matching Engine\n(Python/Pandas)]
    end

    subgraph "3. LOGIC & DATA (Az Agy)"
        AOC_SYS[(AOC System / RLB Adatok)]
        AOC_SYS -->|5. NAV Nyitott Tételek Lekérése| MATCH_ENGINE
        
        MATCH_ENGINE -->|6. Fuzzy Matching Logic| DB_CACHE[(Redis / SQL Cache)]
        
        MATCH_ENGINE -->|7a. High Confidence| EXPORT_SVC[Export Service]
        MATCH_ENGINE -->|7b. Low Confidence| HUMAN_TASK[Review Queue]
    end

    subgraph "4. USER INTERFACE (Level 2 Dashboard)"
        HUMAN_TASK -->|Display| WEB_UI[React SPA\n(Matching Dashboard)]
        USER((Könyvelő / Asszisztens)) -->|8. Egy kattintásos jóváhagyás| WEB_UI
        WEB_UI -->|9. Approved Match| EXPORT_SVC
    end

    subgraph "5. INTEGRATION (Kimenet)"
        EXPORT_SVC -->|10. Fájl feltöltése + Metaadatok párosítása| AOC_SYS
    end

    style KEY_VAULT fill:#f96,stroke:#333,stroke-width:2px
    style MATCH_ENGINE fill:#bbf,stroke:#333,stroke-width:2px
    style AOC_SYS fill:#dfd,stroke:#333,stroke-width:2px
```

---

## 2. TECHNIKAI SPECIFIKÁCIÓ ÉS MŰKÖDÉS

### 2.1. Ingestion Layer (A "Barna Boríték" kiváltása)

Ez a réteg felel azért, hogy a különböző forrásokból az adat bekerüljön a rendszerbe.

* **Komponens:** Azure Functions (Python).
* **Konfiguráció (Mapping):** Az Ügyfél <-> Adatforrás (melyik e-mail cím kihez tartozik) összerendeléseket egy **Azure Table Storage** vagy **SQL Database** tárolja.
* **Biztonság (Kritikus):** Az ügyfelek e-mail fiókjaihoz (IMAP) szükséges jelszavakat vagy App Passwordöket **kizárólag** az **Azure Key Vault**-ban tároljuk. A kód soha nem lát jelszót, csak referenciát.
* **Input Filter (Szűrő):** Itt valósul meg a BRD korlátozása. A rendszer ellenőrzi a fájl kiterjesztését és MIME típusát.
  * *Engedélyezett:* `.pdf`, `.jpg`, `.png`, `.jpeg`.
  * *Eldobott:* `.docx`, `.xls`, `.xlsx`, `.zip`. (Ezeket nem mentjük le, logoljuk a "Skipped" státuszt).

### 2.2. AI & OCR (Adatkinyerés)

* **Szolgáltatás:** Azure Document Intelligence (korábban Form Recognizer).
* **Modell:** "Pre-built Invoice Model".
* **Miért ezt?** Mert ez "out-of-the-box" felismeri a szállítót, dátumokat, végösszeget, adószámot anélkül, hogy egyedi sablonokat kéne tanítani (ami drága és lassú lenne). Kezeli a szkennelt képeket és a digitális PDF-eket is.
* **Kimenet:** Strukturált JSON (Header adatok).

### 2.3. Matching Engine (A "Lelke" a rendszernek)

Ez a komponens végzi el az asszisztens ("Orbita") jelenlegi munkáját.

* **Technológia:** Python (Pandas könyvtár adatmanipulációra + TheFuzz könyvtár a fuzzy matchinghez).
* **Folyamat:**
  1. A rendszer lekéri az AOC-ből (API-n vagy DB nézeten) az adott ügyfélhez tartozó, NAV-ból beérkezett, de még számlakép nélküli tételeket.
  2. **Összehasonlítási Algoritmus:**

      * *Hard Match:* Adószám egyezik ÉS (Sorszám pontos egyezés VAGY (Bruttó összeg egyezés + Dátum egyezés)). -> **Automatikus siker.**
      * *Soft Match:* Adószám egyezik, de az összegben van 1-2 Ft eltérés (kerekítés) VAGY a sorszámban van elütés/karakterhiba. -> **Emberi ellenőrzés szükséges.**
      * *No Match:* Nem található NAV adat (pl. külföldi számla, vagy a NAV rendszer késik). -> **Manuális kezelés.**

### 2.4. Level 2 Dashboard (UI)

A BRD-ben kért egyszerűsített felület.

* **Tech Stack:** React (SPA) + Azure Static Web Apps.
* **Funkció:** Egy "Tinder-szerű" felület a számláknak.
  * Balra: A számla képe.
  * Jobbra: "Szerintünk ez a NAV tétel tartozik hozzá."
  * Gombok: [JÓVÁHAGYÁS] / [ELVETÉS/JAVÍTÁS].

### 2.5. Kimenet (Integráció)

* **Cél:** AOC System.
* **Művelet:** A jóváhagyott párosítás után a rendszer beküldi a fájlt az AOC-be, és a metaadatokban beállítja a kapcsolatot a NAV tétellel (Matching ID).

### 2.6. Hibakezelés és Megbízhatóság (Resilience)

* **Retry Logic (Újrapróbálkozás):** Ha az AOC API vagy a NAV szolgáltatás átmenetileg nem elérhető (pl. 503 Service Unavailable), a rendszer "Exponential Backoff" stratégiával (késleltetett újrapróbálkozás) kísérli meg a műveletet 3 alkalommal.
* **Dead Letter Queue (DLQ):** Ha a 3. próbálkozás is sikertelen, vagy a hiba nem javítható (pl. hibás fájlformátum), az üzenet egy technikai hibalistára (DLQ) kerül, ahonnan a rendszergazda vizsgálhatja ki, így az adat nem veszik el.

---

## 3. ADATVÉDELEM ÉS BIZTONSÁG (Security by Design)

1. **Credential Isolation:** Az ügyfelek e-mail hozzáférései (IMAP) a legérzékenyebb pontok. Ezeket *Secret Rotation* szabályzattal a Key Vault védi.
2. **Zero Data Retention (Hosszú távon):** A rendszer **Stateless**. A feldolgozás és az AOC-be való sikeres feltöltés után a számlaképek törlődnek az Azure Blob Storage-ból. Nem építünk "árnyék-könyvelést", az adatgazda az AOC marad.
3. **Audit Log:** Minden műveletről (Letöltés -> OCR -> Párosítás -> Feltöltés) napló készül, de személyes adatokat (pl. magánszemély neve a számlán) a log nem tartalmaz, csak a tranzakció ID-kat.

## 4. SZÜKSÉGES ELŐFELTÉTELEK (Prerequisites)

Ahhoz, hogy ezt a rendszert a szállító felépíthesse, a **Grekonto-nak biztosítania kell**:

1. **AOC API Dokumentáció:** Vagy hozzáférés az adatbázishoz (Read-Only View), hogy a NAV tételeket le tudjuk kérdezni a párosításhoz. (Ez kritikus függőség!)
2. **Teszt Fiókok:**

    * 1 db dedikált Gmail fiók (IMAP teszthez).
    * 1 db Google Drive mappa.
    * Teszt hozzáférés az AOC-hez.

Ez a terv készen áll a fejlesztők számára a Sprint 1 megkezdéséhez.

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 2.1
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v2.1** (2025-11-22): Resilience komponensek (DLQ, Secret Rotation, Durable Functions) már implementálva
* **v2.0** (2025-11-19): Final BRD v1.2 aligned
* **v1.0** (2025-11-15): Eredeti verzió
