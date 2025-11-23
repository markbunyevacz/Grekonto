# PROJECT SCOPE & PRIORITIES

**Projekt:** Grekonto AI Automatizáció
**Dátum:** 2025.11.19.
**Verzió**: 1.1
**Utolsó frissítés**: 2025-11-22
**Commit**: c72f14bc

Ez a dokumentum rögzíti a projekt elfogadott hatókörét (scope) és a megvalósítási prioritásokat.

## 1. PRIORITÁS (Proof of Concept / Induló fázis): Adatbegyűjtés és központosítás

Ez a kezdő lépés, amely a legkritikusabb "fájdalompontot" (a sokféle forrásból érkező dokumentumok kezelése) oldja meg.

### 1.1. Bemeneti források egységesítése

A rendszer automatikusan begyűjti a bizonylatokat és számlákat a következő csatornákról:

* **Google Drive**
* **E-mail csatolmányok**
* **Dropbox**
* **Egyéb fájlmegosztók**

### 1.2. Dokumentumok központosítása

A begyűjtött dokumentumok automatikus eljuttatása a célrendszerbe (AUC System / Audit Cloud).

### 1.3. Alapadatok kinyerése (Header szint)

A számlákról a fejléc (header) szintű adatok kinyerése a könyvelés előkészítéséhez és az azonosításhoz:

* Számla kelte
* Sorszám
* Szállító neve / Adószáma (Partner azonosítás)
* Végösszeg (Nettó/Bruttó)
* Pénznem
* Speciális jelzések (pl. pénzforgalmi elszámolás, EPR díj, fordított ÁFA jelzése).

### 1.4. Formátumkezelés

* Digitális PDF-ek kezelése.
* Szkennelt (kép alapú) PDF-ek felismerése (OCR).

### 1.5. Validálás

Annak felismerése, hogy az adott dokumentum valóban számla-e, vagy egyéb irreleváns dokumentum.

## 2. RESILIENCE & RELIABILITY (Megbízhatóság) - IMPLEMENTÁLVA ✅

Ez a komponens az 1. prioritás részeként implementálva van, biztosítva a rendszer megbízhatóságát és hibatűrésének.

### 2.1. Dead Letter Queue (DLQ)
* **Cél:** Sikertelen feldolgozások kezelése adatvesztés nélkül
* **Működés:** 3 retry után a sikertelen dokumentumok a DeadLetterQueue táblába kerülnek
* **API:** `GET /api/dlq` (elemek lekérése), `POST /api/dlq/resolve` (feloldás)
* **Audit:** Minden DLQ esemény naplózva

### 2.2. Secret Rotation
* **Cél:** Jelszavak és API kulcsok havi automatikus rotálása
* **Működés:** Timer trigger az 1. nap 00:00-kor
* **Tárolás:** Azure Key Vault
* **API:** `GET /api/secret-status` (status lekérése)

### 2.3. Durable Functions Orchestrator
* **Cél:** Jobb koordináció és state management
* **Workflow:** OCR Activity → Matching Activity → Upload Activity
* **API:** `GET /api/orchestration-status` (status lekérése)
* **State Management:** Teljes orchestration state nyomon követés

### 2.4. Audit Logging
* **Naplózás:** Minden feldolgozási lépés naplózva
* **Particionálás:** Napi particionálás (YYYYMMDD)
* **Adatvédelem:** Csak metaadatok, személyes adatok nincsenek naplózva

---

## 3. PRIORITÁS: Számlázás automatizálása

* **Excel kiváltása:** A jelenlegi manuális, Excel-alapú számlázási előkészítés automatizálása.
* **Dinamikus adatkapcsolat:** Összekapcsolás a bérszámfejtési adatokkal és az ügyfél státuszával.
* **Tömeges számlagenerálás:** Feladó tábla automatikus elkészítése a számlázó program (Számlázz.hu) felé.

## 4. PRIORITÁS: Ügyfélportál és Ügyfél-történet (History)

* **Ügyfél életút követése:** Visszakereshető ügyfél történet (díjak, emelések).
* **Szerződéses paraméterek tárolása:** Aktív/inaktív státusz, ÁFA kör, riportolási igények.
* **Automatikus árazási javaslatok:** Javaslattétel áremelésre historikus adatok alapján.

## 5. PRIORITÁS: Ad-hoc feladatkezelés és E-mail menedzsment

* **E-mailből feladat:** Beérkező e-mailek automatikus kategorizálása és feladattá konvertálása.
* **Felelősök hozzárendelése:** Feladatok automatikus kiosztása.

## KIZÁRT ELEMEK (Out of Scope)

* **Tételes feldolgozás (Line items):** Tételek automatikus főkönyvi számra sorolása.
* **Munkavégzés profilozása/figyelése:** Folyamatok mérése (időráfordítás).
* **Kézírás felismerés:** Nem elvárás.

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)
**Verzió:** 1.1

### Frissítési Történet
* **v1.1** (2025-11-22): Resilience & Reliability (2. prioritás) hozzáadva - DLQ, Secret Rotation, Durable Functions, Audit Logging
* **v1.0** (2025-11-19): Eredeti verzió
