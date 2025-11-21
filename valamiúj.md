## Grekonto AI Automatizációs Rendszer
A Grekonto AI automatizációs rendszer teljes működési ciklusát bemutató codemap, a dokumentum beérkezéstől a párosítási döntésig. Kulcsfontosságú helyek: időzített email figyelés [1a], OCR feldolgozás [2b], intelligens párosítási algoritmus [3b], React alapú felhasználói felület [5a], és a manuális döntéshozatali folyamat [6c].
### 1. Dokumentum Beérkezés és Feldolgozás Indítása
Email beérkezés időzített figyelése és csatolmányok kinyerése a feldolgozási folyamat elindításához
### 1a. Időzített Email Figyelés Indítása (`__init__.py:7`)
Azure Function timer trigger indítása email források lekérdezésére
```text
def main(mytimer: func.TimerRequest) -> None:
```
### 1b. Csatolmányok Letöltése (`__init__.py:26`)
IMAP kliens hívása a csatolmányok kinyerésére
```text
attachments = imap_client.fetch_attachments(source)
```
### 1c. Fájltípus Szűrés (`__init__.py:33`)
Csak támogatott formátumok engedélyezése a BRD szerint
```text
if not filename.lower().endswith(('.pdf', '.jpg', '.png', '.jpeg')):
```
### 1d. Feltöltés Blob Storage-be (`__init__.py:39`)
Fájlok mentése a feldolgozási folyamat számára
```text
storage_client.upload_to_blob("raw-documents", blob_name, content)
```
### 2. OCR Feldolgozás és Adatkinyerés
Blob trigger által indított Document Intelligence feldolgozás a számlaadatok kinyerésére
### 2a. Blob Trigger Indítás (`__init__.py:11`)
Új dokumentum érkezésekor automatikus feldolgozás indítása
```text
def main(myblob: func.InputStream):
```
### 2b. Azure Document Intelligence Hívás (`__init__.py:32`)
Számla modell használata a fejléc adatok kinyerésére
```text
poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", document=blob_content)
```
### 2c. Adatok Kinyerése (`__init__.py:40`)
Szállító, összeg, dátum és adószám kinyerése a számlából
```text
extracted_data = {"vendor": invoice.fields.get("VendorName", {}).get("value")
```
### 2d. Párosító Motor Hívása (`__init__.py:54`)
Kinyert adatok továbbítása a párosításra
```text
match_result = matching_engine.find_match(extracted_data)
```
### 3. Intelligens Párosítási Logika
NAV adatokkal való párosítás a hard match, soft match és no match algoritmusok szerint
### 3a. Párosító Függvény Indítása (`matching_engine.py:4`)
Kinyert számlaadatok párosítása a NAV tételekkel
```text
def find_match(extracted_data):
```
### 3b. Hard Match Logika (`matching_engine.py:19`)
Pontos egyezés adószám + összeg alapján (automatikus jóváhagyás)
```text
if item["tax_id"] == vendor_tax_id and item["amount"] == amount:
```
### 3c. Soft Match Tolerancia (`matching_engine.py:26`)
Kerekítési eltérés kezelése (emberi ellenőrzés szükséges)
```text
if abs(item["amount"] - (amount or 0)) <= 5:
```
### 3d. No Match Eset (`matching_engine.py:29`)
Nincs egyezés a NAV adatokban
```text
return {"status": "RED", "reason": "No matching open item found"}
```
### 4. Feladat Mentése és Állapotkezelés
Feldolgozási eredmények mentése Table Storage-be és állapotok kezelése
### 4a. Feladat Adatok Összeállítása (`__init__.py:64`)
Feldolgozási eredmények struktúrálása mentésre
```text
task_data = {"id": blob_name.replace('/', '_').replace('.', '_'), "status": match_result['status']}
```
### 4b. Automatikus Jóváhagyás Kezelése (`__init__.py:73`)
Zöld út esetén automatikus lezárás
```text
if match_result['status'] == 'GREEN': task_data['status'] = 'COMPLETED'
```
### 4c. Mentés Table Storage-be (`__init__.py:78`)
Feladat mentése a felhasználói felület számára
```text
table_service.save_task(task_data)
```
### 4d. Függőben Lévő Feladatok Lekérdezése (`table_service.py:62`)
Csak sárga és piros állapotú feladatok visszaadása
```text
filter_query = "Status eq @status1 or Status eq @status2"
```
### 5. Frontend Dashboard és Feladat Lista
React alapú felhasználói felület a függőben lévő feladatok megjelenítésére és kezelésére
### 5a. Feladatok Lekérdezése (`Dashboard.tsx:26`)
API hívás a függőben lévő feladatok lekérdezésére
```text
fetch('/api/tasks').then(res => res.json()).then(data => { setTasks(data);
```
### 5b. Feladatok Szűrése (`Dashboard.tsx:38`)
Sárga/piros állapotú feladatok szűrése a UX specifikáció szerint
```text
const filteredTasks = tasks.filter(t => { if (filter === 'ALL') return true; return t.status === filter;
```
### 5c. Navigáció a Párosító Felületre (`Dashboard.tsx:179`)
Link a részletes párosító nézetre a feladat azonosítójával
```text
to={`/matcher?taskId=${task.id}`} className="inline-flex items-center gap-1 text-indigo-600"
```
### 6. Párosító Felület és Döntéshozatal
Split-screen felület a dokumentum ellenőrzésére és a párosítási döntések meghozatalára
### 6a. Feladat Betöltése (`Matcher.tsx:42`)
Konkrét feladat adatainak lekérdezése az azonosító alapján
```text
fetch('/api/tasks').then((data: Task[]) => { const found = data.find(t => t.id === taskId);
```
### 6b. Dokumentum Megjelenítése (`Matcher.tsx:116`)
SAS URL segítségével a számlakép bal oldali megjelenítése
```text
src={task.document_url} alt="Document" className="max-w-full shadow-lg"
```
### 6c. Billentyűzatos Gyorsító (`Matcher.tsx:71`)
Enter gombbal gyors jóváhagyás a UX irányelvek szerint
```text
if (e.key === 'Enter') { handleDecision('approve'); }
```
### 6d. Döntés Elküldése (`Matcher.tsx:85`)
Feladat állapotának frissítése a jóváhagyás/elvetés után
```text
await fetch(`/api/tasks/${task.id}/status`, { method: 'POST', body: JSON.stringify({ status: newStatus })
```
### 7. Manuális Feltöltés és Forráskezelés
Drag & drop feltöltés és email források konfigurációja a beállítások felületen
### 7a. Fájl Feltöltése (`Dashboard.tsx:52`)
Manuális dokumentum feltöltése a drag & drop zónából
```text
await fetch('/api/upload', { method: 'POST', headers: { 'x-filename': file.name }, body: file
```
### 7b. Fájl Fogadása a Backenden (`__init__.py:23`)
Feltöltött fájl kezelése az Azure Functionben
```text
file_content = req.get_body() filename = req.headers.get('x-filename')
```
### 7c. Források Listázása (`Settings.tsx:7`)
Email és Drive források megjelenítése a beállításokban
```text
sources = [{ type: 'IMAP', name: 'kovacs@ceg.hu', client: 'Kovács Bt.', status: 'OK' }
```
### 7d. IMAP Kapcsolat és Keresés (`imap_client.py:32`)
Email fiókhoz csatlakozás és olvasatlan üzenetek keresése
```text
mail.login(user, password) mail.select("inbox") status, messages = mail.search(None, "UNSEEN")
```