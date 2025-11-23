# TO-BE PROCESS (Jövőbeli Folyamat)

**Projekt**: Grekonto AI Automatizáció
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-22
**Commit**: c72f14bc

A korábbi egyeztetések és a technikai tervezés alapján összeállítottam a **Jövőbeli Folyamat (TO-BE Process)** leírását. Ez a leírás azt mutatja be, hogyan fog kinézni a napi munka a rendszer élesítése után, felhasználói szemszögből.

A folyamatot 4 logikai lépésre bontottam. A legfontosabb változás, hogy a **manuális keresgélés és párosítás helyett a rendszer előkészít, az ember pedig csak dönt.**

---

## 1. FÁZIS: Az Automatikus Begyűjtés (Ingestion)

*A cél: Az "Orbita" (asszisztens) tehermentesítése a letöltögetéstől.*

A rendszer a háttérben, emberi beavatkozás nélkül, folyamatosan (pl. 15 percenként) figyeli a forrásokat:

1. **Központi e-mailek:** Megnézi a Grekonto közös email fiókjait.
2. **Ügyfél e-mailek:** (A "Barna borítékos" ügyfeleknél) Belép az ügyfél dedikált fiókjába.
3. **Google Drive/Dropbox:** Figyeli az ügyfelek által feltöltött mappákat.
4. **Manuális feltöltés:** Ha papírt kaptatok, azt az asszisztens beszkenneli és csak "behúzza" a rendszer ablakába (Drag & Drop).

**Mit csinál a rendszer?**

* Kiválogatja a PDF és Képfájlokat (számlákat).
* A Word, Excel, ZIP fájlokat **figyelmen kívül hagyja** (ezeket nem dolgozza fel).
* A letöltött fájlokat beküldi a feldolgozó motorba.

---

## 2. FÁZIS: Az "Olvasás" és Értelmezés (AI Processing)

*A cél: Adatok kinyerése a képből.*

A rendszer "ránéz" a dokumentumra (legyen az digitális PDF vagy egy gyűrött számla fotója), és az AI segítségével kiolvassa a fejléc adatokat:

* **Ki a szállító?** (Név, Adószám)
* **Mikor?** (Kelt, Teljesítés)
* **Mennyi?** (Bruttó végösszeg, Pénznem)
* **Mi a sorszám?**

*Fontos:* Nem olvassa el, hogy "citrom" vagy "WC illatosító" van-e rajta, csak a számla keretadatait.

---

## 3. FÁZIS: A Nagy Párosítás (The Matching Engine) – A LÉNYEG

*A cél: A NAV adatok és a Kép összekötése.*

Ez a folyamat "agya". A rendszer megkérdezi az AOC/RLB rendszert: *"Van nálad olyan nyitott tétel a NAV-ból, ami ehhez a szállítóhoz és ehhez az összeghez tartozik?"*

Itt három dolog történhet (mint egy közlekedési lámpa):

* 🟢 **ZÖLD ÚT (Perfect Match):**
  * A rendszer talál egyetlen, tökéletesen illeszkedő NAV tételt (Adószám + Összeg + Sorszám/Dátum stimmel).
  * **Akció:** A rendszer **automatikusan** feltölti a képet az AOC-be, és hozzácsatolja a NAV tételhez.
  * **Emberi teendő:** Semmi. A könyvelő már készen látja a rendszerben.

* 🟡 **SÁRGA ÚT (Bizonytalan Match):**
  * A rendszer talál hasonlót, de nem biztos benne (pl. 1 Ft kerekítési eltérés van, vagy a sorszámban van egy elütés, vagy több azonos összegű számla van).
  * **Akció:** A rendszer beküldi ezt az esetet az "Ellenőrző Műszerfalra" (Dashboard).
  * **Emberi teendő:** Döntés szükséges (lásd 4. fázis).

* 🔴 **PIROS ÚT (No Match):**
  * A rendszer nem talál NAV adatot (pl. külföldi számla, vagy még nem ért át a NAV-on).
  * **Akció:** A rendszer "Feldolgozandó / Ismeretlen" státusszal jelöli meg.
  * **Emberi teendő:** Manuális kezelés (lásd 4. fázis).

---

## 4. FÁZIS: Az Asszisztensi Műszerfal (Level 2 User Interface)

*A cél: A kivételek gyors kezelése.*

A "Level 2" szintű kolléga (aki nem IT szakértő) megnyit egy egyszerű webes felületet. Itt **kizárólag a Sárga és Piros** eseteket látja.

**Hogyan néz ki a munka?**
A képernyő ketté van osztva:

* **Bal oldalon:** Látja a számla képét.
* **Jobb oldalon:** A rendszer kiírja: *"Szerintem ez a NAV tétel tartozik hozzá (90% biztosság). Elfogadod?"*

**A felhasználó lehetőségei:**

1. **"Igen, párosítsd!" (Gomb):** Egy kattintás, és a rendszer végrehajtja a feltöltést.
2. **"Nem, ez másik."**: Kiválaszthatja manuálisan a listából a jót.
3. **"Ez nem számla / Kuka":** Ha a rendszer tévedésből egy reklámanyagot dolgozott fel.

---

### Összefoglalva: Mi változik a hétköznapokban?

| Tevékenység | MOST (As-Is) | EZUTÁN (To-Be) |
| :--- | :--- | :--- |
| **E-mailek letöltése** | Asszisztens lépked be fiókokba, menti le a fájlokat. | **Automata.** (A gép csinálja a háttérben). |
| **Drive figyelés** | Asszisztens nézegeti, jött-e új fájl. | **Automata.** |
| **Párosítás** | Asszisztens/Könyvelő keresgél: *"Ez a kép melyik tételhez tartozik?"* | **Automata (Zöld út)** vagy **Támogatott döntés (Sárga út).** |
| **Adatrögzítés** | Kézi feltöltés és csatolás. | **Automata** a jóváhagyás után. |
| **Fókusz** | Adminisztráció és fájlmozgatás. | Csak a **problémás esetek** kezelése. |

Ez a folyamat biztosítja, hogy a Grekonto által kért "Level 2" felhasználói élmény megvalósuljon, a "Barna borítékos" ügyfelek problémája megoldódjon, és a munka oroszlánrészét az algoritmus végezze el.

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v1.0** (2025-11-22): Eredeti verzió - Teljes TO-BE folyamat dokumentálva
