# Grekonto AI Automatizációs Rendszer - CodeMap

A Grekonto AI automatizációs rendszer teljes működési ciklusát bemutató térkép, a dokumentum beérkezéstől a párosítási döntésig.

### 1. Dokumentum Beérkezés és Feldolgozás Indítása
**Hely**: `backend/ingestion_timer/__init__.py`

Email beérkezés időzített figyelése és csatolmányok kinyerése a feldolgozási folyamat elindításához.

#### 1a. Időzített Email Figyelés Indítása (Line 11)
Azure Function timer trigger indítása email források lekérdezésére.
```python
def main(mytimer: func.TimerRequest) -> None:
```

#### 1b. Csatolmányok Letöltése (Line 44)
IMAP kliens hívása a csatolmányok kinyerésére.
```python
files = imap_client.fetch_attachments(email_config)
```

#### 1c. Fájltípus Szűrés (Line 57)
Csak támogatott formátumok engedélyezése a BRD szerint.
```python
if not filename.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg')):
```

#### 1d. Feltöltés Blob Storage-be (Line 63)
Fájlok mentése a feldolgozási folyamat számára.
```python
storage_client.upload_to_blob("raw-documents", blob_name, content)
```

### 2. OCR Feldolgozás és Adatkinyerés
**Hely**: `backend/process_document/__init__.py`

Blob trigger által indított Document Intelligence feldolgozás a számlaadatok kinyerésére.

#### 2a. Blob Trigger Indítás (Line 12)
Új dokumentum érkezésekor automatikus feldolgozás indítása.
```python
def main(myblob: func.InputStream):
```

#### 2b. Azure Document Intelligence Hívás (Line 33)
Számla modell használata a fejléc adatok kinyerésére.
```python
poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", document=blob_content)
```

#### 2c. Adatok Kinyerése (Line 52)
Szállító, összeg, dátum és adószám kinyerése a számlából.
```python
extracted_data = {
    "vendor": invoice.fields.get("VendorName", {}).get("value"),
    # ...
}
```

#### 2d. Párosító Motor Hívása (Line 67)
Kinyert adatok továbbítása a párosításra.
```python
match_result = matching_engine.find_match(extracted_data)
```

### 3. Intelligens Párosítási Logika
**Hely**: `backend/shared/matching_engine.py`

NAV adatokkal való párosítás a hard match, soft match és no match algoritmusok szerint.

#### 3a. Párosító Függvény Indítása (Line 6)
Kinyert számlaadatok párosítása a NAV tételekkel.
```python
def find_match(extracted_data):
```

#### 3b. Hard Match Logika (Line 32)
Pontos egyezés adószám + összeg alapján (automatikus jóváhagyás).
```python
if item.get("tax_id") == vendor_tax_id and item.get("amount") == amount:
```

#### 3c. Soft Match Tolerancia (Line 44)
Kerekítési eltérés kezelése (emberi ellenőrzés szükséges).
```python
if abs(item.get("amount", 0) - (amount or 0)) <= 5:
```

#### 3d. No Match Eset (Line 56)
Nincs egyezés a NAV adatokban.
```python
return {"status": "RED", "reason": "No matching open item found"}
```

### 4. Feladat Mentése és Állapotkezelés
**Hely**: `backend/process_document/__init__.py` & `backend/shared/table_service.py`

Feldolgozási eredmények mentése Table Storage-be és állapotok kezelése.

#### 4a. Feladat Adatok Összeállítása (Line 85)
Feldolgozási eredmények struktúrálása mentésre.
```python
task_data = {
    "id": blob_name.replace('/', '_').replace('.', '_'),
    "status": match_result['status'],
    # ...
}
```

#### 4b. Automatikus Jóváhagyás Kezelése (Line 95)
Zöld út esetén automatikus lezárás.
```python
if match_result['status'] == 'GREEN':
    task_data['status'] = 'COMPLETED'
```

#### 4c. Mentés Table Storage-be (Line 100)
Feladat mentése a felhasználói felület számára.
```python
table_service.save_task(task_data)
```

#### 4d. Függőben Lévő Feladatok Lekérdezése (table_service.py:245)
Csak sárga és piros állapotú feladatok visszaadása.
```python
filter_query = f"PartitionKey eq '{pk}' and (Status eq @status1 or Status eq @status2)"
```

### 5. Frontend Dashboard és Feladat Lista
**Hely**: `frontend/src/pages/Dashboard.tsx`

React alapú felhasználói felület a függőben lévő feladatok megjelenítésére és kezelésére.

#### 5a. Feladatok Lekérdezése (Line 26)
API hívás a függőben lévő feladatok lekérdezésére.
```typescript
fetch('/api/tasks').then(res => res.json()).then(data => { setTasks(data);
```

#### 5b. Feladatok Szűrése (Line 38)
Sárga/piros állapotú feladatok szűrése a UX specifikáció szerint.
```typescript
const filteredTasks = tasks.filter(t => {
  if (filter === 'ALL') return true;
  return t.status === filter;
});
```

#### 5c. Navigáció a Párosító Felületre (Line 180)
Link a részletes párosító nézetre a feladat azonosítójával.
```typescript
to={`/matcher?taskId=${task.id}`}
```

### 6. Párosító Felület és Döntéshozatal
**Hely**: `frontend/src/pages/Matcher.tsx`

Split-screen felület a dokumentum ellenőrzésére és a párosítási döntések meghozatalára.

#### 6a. Feladat Betöltése (Line 43)
Konkrét feladat adatainak lekérdezése az azonosító alapján.
```typescript
fetch('/api/tasks').then(res => res.json()).then((data: Task[]) => { 
    const found = data.find(t => t.id === taskId);
```

#### 6b. Dokumentum Megjelenítése (Line 134)
SAS URL segítségével a számlakép bal oldali megjelenítése.
```typescript
src={task.document_url} alt="Document" className="max-w-full shadow-lg"
```

#### 6c. Billentyűzatos Gyorsító (Line 72)
Enter gombbal gyors jóváhagyás a UX irányelvek szerint.
```typescript
if (e.key === 'Enter') { handleDecision('approve'); }
```

#### 6d. Döntés Elküldése (Line 87)
Feladat állapotának frissítése a jóváhagyás/elvetés után.
```typescript
await fetch(`/api/tasks/${task.id}/status`, { 
    method: 'POST', 
    body: JSON.stringify({ status: newStatus })
```

### 7. Manuális Feltöltés és Forráskezelés
**Hely**: `frontend/src/pages/Dashboard.tsx`, `Settings.tsx` & `backend/api_upload_document/__init__.py`

Drag & drop feltöltés és email források konfigurációja a beállítások felületen.

#### 7a. Fájl Feltöltése (Dashboard.tsx:52)
Manuális dokumentum feltöltése a drag & drop zónából.
```typescript
await fetch('/api/upload', { 
    method: 'POST', 
    headers: { 'x-filename': file.name }, 
    body: file
```

#### 7b. Fájl Fogadása a Backenden (api_upload_document/__init__.py:23)
Feltöltött fájl kezelése az Azure Functionben.
```python
if not file_content:
    filename_header = req.headers.get('x-filename')
```

#### 7c. Források Listázása (Settings.tsx:24)
Email és Drive források megjelenítése a beállításokban.
```typescript
const res = await fetch('/api/settings/sources');
```

#### 7d. IMAP Kapcsolat és Keresés (imap_client.py:31)
Email fiókhoz csatlakozás és olvasatlan üzenetek keresése.
```python
mail = imaplib.IMAP4_SSL(host)
mail.login(user, password)
mail.select("inbox")
status, messages = mail.search(None, "UNSEEN")
```

