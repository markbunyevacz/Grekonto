# USER EXPERIENCE (Felhasználói Élmény)

**Projekt**: Grekonto AI Automatizáció
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-22
**Commit**: TBD (frissítés után)

Senior BA és UX (User Experience) tervező sapkában elkészítettem a **Level 2-es felhasználói élményre** tervezett felületek vázlatát (Wireframe) és működési leírását.

A vezérelvünk a **"Zero-Training Interface"** volt: azaz, ha leültetünk egy új kollégát a gép elé, 5 perc alatt értse, mit kell tennie, betanítás nélkül.

Íme a 3 fő képernyő terve:

---

## 1. KÉPERNYŐ: A "Teendő Lista" (Queue Dashboard)

Ez a nyitóoldal. Itt nem látunk minden számlát, **csak azokat, ahol emberi döntés szükséges** (a "Sárga" és "Piros" utat bejárt tételek). A "Zöld" (sikeresen párosított) tételek már automatikusan az AOC-ben vannak, itt nem zavarják a felhasználót.

**UI Vázlat:**

```text
+-----------------------------------------------------------------------+
|  GREKONTO AI MATCHER                                  Felhasználó: Orbita |
+-----------------------------------------------------------------------+
|  MAI STATISZTIKA:                                                     |
|  ✅ 142 Automatikusan feldolgozva | ⚠️ 12 Ellenőrzésre vár             |
+-----------------------------------------------------------------------+
|                                                                       |
|  ELLENŐRZÉSRE VÁRÓ TÉTELEK (12 db)                                    |
|                                                                       |
|  [ Szűrők: Mind | Csak Sárga (Bizonytalan) | Csak Piros (Nincs Match) ] |
|                                                                       |
|  Státusz | Beérkezés ideje | Szállító (AI tipp) | Összeg      | Akció   |
|  --------+-----------------+--------------------+-------------+---------|
|  🟡 85%  | Ma, 08:15       | MVM Next Zrt.      | 14.200 Ft   | [Nyitás]|
|  🟡 72%  | Ma, 09:30       | Praktiker Kft.     | 45.990 Ft   | [Nyitás]|
|  🔴 0%   | Tegnap, 16:00   | Unknown (Külföldi) | 120 EUR     | [Nyitás]|
|  ...                                                                  |
+-----------------------------------------------------------------------+
```

**Működés:**

* A lista csökkenő sorrendben mutatja a feladatokat.
* A "Státusz" oszlopban színkód (Sárga/Piros) jelzi a probléma jellegét.
* A [Nyitás] gomb visz a részletes nézetre.

---

## 2. KÉPERNYŐ: A Párosító Felület (The Matcher) – A FŐ MUNKAESZKÖZ

Ez az a felület, amit az "Asszisztens" a nap 90%-ában látni fog. Kétosztatú képernyő (Split Screen).

**UI Vázlat:**

```text
+---------------------------------------+---------------------------------------+
|  < Vissza a listához                  |  Párosítás Jóváhagyása                |
+---------------------------------------+---------------------------------------+
|                                       |                                       |
|           (DOKUMENTUM KÉPE)           |   1. AI ÁLTAL FELISMERT ADATOK:       |
|                                       |   ---------------------------------   |
|   +-------------------------------+   |   Szállító:   MVM Next Zrt.           |
|   |                               |   |   Dátum:      2024.11.15              |
|   |   SZÁMLA                      |   |   Sorszám:    MVM-2024/888            |
|   |                               |   |   Végösszeg:  14.200 Ft               |
|   |   MVM Next                    |   |                                       |
|   |   Végösszeg: 14.200 Ft        |   =================================   |
|   |                               |                                       |
|   |   Sorszám: MVM-2024/888       |   2. NAV (AOC) TALÁLAT (Javaslat):    |
|   |                               |   ---------------------------------   |
|   |                               |   🟢 EGYEZÉS VALÓSZÍNŰSÉGE: MAGAS     |
|   |                               |                                       |
|   +-------------------------------+   |   [X] Kiválasztva:                    |
|                                       |       MVM Next Zrt. (10893...)        |
|   [Nagyítás] [Forgatás]               |       Dátum: 2024.11.15               |
|                                       |       Összeg: 14.200 Ft               |
|                                       |       (NAV Státusz: Beérkezett)       |
|                                       |                                       |
+---------------------------------------+---------------------------------------+
|                                                                               |
|   [ 🗑️ ELVETÉS (Kuka) ]    [ 🔍 KÉZI KERESÉS ]    [ ✅ JÓVÁHAGYÁS & BEKÜLDÉS ] |
|                                                                               |
+---------------------------------------+---------------------------------------+
```

**Működés (Level 2 szemlélet):**

* **Bal oldal:** A PDF/Kép látható, nagyítható.
* **Jobb oldal (Felső rész):** Mit olvasott le a gép? (Ellenőrizhető, hogy jól látta-e az összeget).
* **Jobb oldal (Alsó rész):** Mit talált a NAV rendszerben? Ha a rendszer talált valamit, azt automatikusan kijelöli.
* **Gombok:** Hatalmas, egyértelmű gombok alul.
  * **Jóváhagyás:** Ha stimmel, egy kattintás, és a fájl repül az AOC-be a NAV tételhez csatolva.
  * **Kézi keresés:** Ha a gép rossz NAV tételt ajánlott fel (lásd 3. képernyő).
  * **Elvetés:** Ha ez nem is számla (pl. reklámlevél).

---

## 3. KÉPERNYŐ: Manuális Keresés (Manual Lookup)

Ez akkor jön elő, ha a fenti képernyőn a "Kézi keresés" gombra kattintunk, mert a gép nem találta meg a párját.

**UI Vázlat:**

```text
+-----------------------------------------------------------------------+
|  KÉZI PÁROSÍTÁS KERESÉSE                                     [X] Bezár|
+-----------------------------------------------------------------------+
|  A rendszer nem talált egyezést. Kérlek keress a NAV tételek között!  |
|                                                                       |
|  Keresés: [ MVM Next             ]  [ 14200       ]   [ Keresés ]     |
|                                                                       |
|  TALÁLATOK:                                                           |
|  [ ] MVM Next Zrt. | 2024.11.15 | 14.200 Ft | Sorszám: ...888         |
|  [ ] MVM Next Zrt. | 2024.10.15 | 14.200 Ft | Sorszám: ...777         |
|                                                                       |
|                                            [ PÁROSÍTÁS EZZEL A TÉTELLEL ] |
+-----------------------------------------------------------------------+
```

**Működés:**

* A felhasználó beírhatja a szállító nevét vagy az összeget.
* A rendszer listázza a NAV-ban lévő nyitott tételeket.
* A felhasználó kiválasztja a helyeset, és összeköti.

Ez a felület biztosítja, hogy még a legbonyolultabb eseteket is meg lehessen oldani anélkül, hogy ki kellene lépni az Excelbe vagy az AOC-be.

---

### Összefoglalás: Mit kap a Grekonto?

A fejlesztés részeként nem csak a "kódot" kapjátok meg, hanem ezt a **Frontend Applikációt** is, ami:

1. Webes felületen elérhető (böngészőből).
2. Reszponzív (akár tableten is nyomkodható az ebédszünetben, ha sürgős).
3. Kifejezetten a **"kattints és haladj"** logikára épül, minimalizálva a gépelést.

Ez a UI terv része a Senior Architect által korábban vázolt "User Interface" doboznak, és a BA által definiált "Level 2" követelménynek.

Senior UI/UX Designer és Frontend Lead sapkában válaszolok. Mivel a célcsoport "Level 2" felhasználók (nem IT szakemberek, hanem könyvelési asszisztensek), a dizájnnak a **funkcionális minimalizmust** kell követnie.

Nem lehet "csicsás", mert ez egy munkaeszköz. Olyannak kell lennie, mint egy jól szervezett műszerfal: tiszta, kontrasztos, megnyugtató.

Íme a javasolt technológiai és design specifikáció:

---

## 1. TECHNOLÓGIAI STACK (Miből épüljön?)

A Senior Architect által meghatározott React alapokra építkezünk, de modern eszközökkel:

* **Keretrendszer:** **React** (TypeScripttel). Ez a standard, stabil, gyors.
* **UI Komponens Könyvtár:** **shadcn/ui** + **Tailwind CSS**.
  * *Miért ez?* Jelenleg ez a legmodernebb iparági standard. "LEGO kockákat" ad (gombok, inputok, kártyák), amik gyönyörűek, hozzáférhetőek (akadálymentesek) és teljesen testreszabhatók. Nem néz ki "bóvlinak", mint egy alap Bootstrap.
* **PDF Megjelenítő:** **react-pdf**. Lehetővé teszi, hogy a PDF-et ne egy külön ablakban nyissa meg, hanem beágyazva a felületbe, ahol nagyítható és forgatható.
* **Ikonkészlet:** **Lucide React**. Vékony vonalas, modern, nagyon tiszta ikonok.
* **State Management:** **TanStack Query**. Hogy az adatok (listák) azonnal frissüljenek, ha a háttérben az AI dolgozik.

---

## 2. DESIGN NYELV (Visual Identity)

A **"Clean Enterprise"** stílust követjük.

* **Színhasználat (Color Palette):** A pénzügyi bizalom színei.
  * **Háttér:** Törtfehér / Világosszürke (`#F8FAFC` - Slate-50). Nem bántja a szemet 8 óra munka alatt sem.
  * **Elsődleges (Primary):** Sötétkék / Indigó (A Grekonto brand színeihez igazítva). Ez a "Művelet" színe.
  * **Siker (Match):** Smaragdzöld (Emerald). Nem rikító zöld, hanem nyugodt, sötétebb zöld.
  * **Figyelmeztetés (Review):** Borostyán (Amber). A sárga tételekhez.
  * **Veszély (No Match/Delete):** Rózsa (Rose). A piros tételekhez.
* **Tipográfia:** **Inter** vagy **Geist Sans**. Ezek a legjobban olvasható modern fontok képernyőn, kiválóan olvashatóak a számok (táblázatoknál kritikus!).
* **Elrendezés (Layout):**
  * **High Density (Nagy sűrűség):** Nem pazaroljuk a helyet nagy margókkal. Az asszisztensnek sok adatot kell látnia egyszerre, görgetés nélkül.
  * **Split View (Osztott nézet):** A képernyő mindig felezett a munkafolyamat során (Balra a dokumentum, jobbra az adat).

---

## 3. HIÁNYZÓ KÉPERNYŐK (Additional Screens)

A korábban említett 3 fő képernyő (Lista, Párosító, Kézi kereső) mellé a következőkre lesz szükség a teljes rendszerhez:

### 3.1. Bejelentkezés (Login Screen)

* **Funkció:** Biztonságos belépés. Mivel O365 integrációt említettetek, itt a **"Sign in with Microsoft"** gombnak kell lennie.
* **Design:** Minimalista, középen a Grekonto logó, alatta a Microsoft gomb. Tiszta, profi.

### 3.2. Beállítások / Adatforrások Kezelése (Settings & Sources)

* **Funkció:** Ez kritikus a "Barna borítékos" ügyfelek miatt! Itt kell tudnia az adminnak (pl. Szilvinek) felvenni az új forrásokat.
* **Tartalom:**
  * *Forrás hozzáadása gomb:* (Email vagy Drive).
  * *IMAP adatok megadása:* (Szerver, Felhasználó, Jelszó/App Password mezők - jelszó kipontozva).
  * *Ügyfél hozzárendelése:* Melyik ügyfélhez tartozik ez a forrás? (Legördülő lista az RLB partnerekből).
* **Design:** Űrlap jellegű, validációval (zöld pipa, ha sikeres a teszt csatlakozás).

### 3.3. Előzmények és Napló (Activity Log / History)

* **Funkció:** Ha valaki véletlenül félrekattintott, itt vissza lehet keresni. "Mit csináltam ma délelőtt?"
* **Tartalom:** Egy kereshető táblázat.
  * Oszlopok: Időpont | Fájlnév | Felhasználó | Eredmény (Párosítva / Elvetve) | Művelet (Visszavonás gomb).
* **Design:** Sűrű táblázatos nézet, szűrőkkel a tetején (Dátumra, Felhasználóra).

### 3.4. Manuális Feltöltés (Upload Zone)

* **Funkció:** Ha az asszisztens beszkennel 50 db számlát a gépére, azokat ide húzza be.
* **Design:** Lehet egy külön menüpont, vagy a Dashboard tetején egy állandóan elérhető "Drop Zone".
  * *Látvány:* Szaggatott vonalas keret, "Húzd ide a fájlokat" felirat.
  * *Interakció:* Ha behúzol fájlt, kékre vált. Feltöltéskor progress bar (csík) mutatja a folyamatot.

---

## 4. ÖSSZEFOGLALÓ UX IRÁNYELVEK (Guidelines)

1. **Keyboard First:** A "Level 2" felhasználók, ha belejönnek, nagyon gyorsak. Támogatni kell a billentyűzetes vezérlést:

   * `Enter` = Jóváhagyás (Match)
   * `Esc` = Mégse
   * `Nyíl gombok` = Lapozás a listában

2. **Focus State:** Mindig legyen egyértelmű, hol van a fókusz. Ha a "Jóváhagyás" gombon áll, az legyen vastagon keretezve vagy más színű.

3. **Feedback (Visszajelzés):** Minden sikeres művelet után egy apró, nem zavaró üzenet ("Toast notification") a sarokban: *"Számla sikeresen rögzítve"*. Ne ugorjon fel OKéznivaló ablak (Pop-up), mert az lassítja a munkát.

Ez a design csomag biztosítja, hogy a rendszer nemcsak működőképes, hanem szerethető és hatékony munkaeszköz lesz a Grekonto csapatának.

Jogos az észrevétel! Az előbb csak leírtam őket, de a vizuális terv (Wireframe) sokkal beszédesebb.

Íme a **Senior UI/UX Designer** által készített drótvázak a hiányzó funkciókhoz. Ezek követik a korábban meghatározott "Clean Enterprise" stílust és a `shadcn/ui` komponensrendszert.

---

### 3.1. BEJELENTKEZÉS (Login Screen)

**Cél:** Bizalomépítő, végtelenül egyszerű belépés.

```text
+-----------------------------------------------------------------------+
|                                                                       |
|                                                                       |
|                       [ GREKONTO LOGO ]                               |
|                                                                       |
|             Üdvözlünk az AI Automatizációs Rendszerben                |
|                                                                       |
|           +-----------------------------------------------+           |
|           |  [Windows Logo]  Bejelentkezés Microsofttal   |           |
|           +-----------------------------------------------+           |
|                                                                       |
|                                                                       |
|         (Vagy jelentkezz be e-mail címmel - Adminoknak)              |
|         [ E-mail cím               ]                                  |
|         [ Jelszó                   ]                                  |
|         [ BELÉPÉS ]                                                   |
|                                                                       |
|                                                                       |
|       © 2025 Grekonto Könyvelőiroda | Adatvédelem | Support           |
|                                                                       |
+-----------------------------------------------------------------------+
```

**UX Megjegyzés:** A Microsoft gomb a domináns (Primary Button), mivel az O365 integráció volt az alapigény. A jelszavas rész csak "fallback" opció.

---

### 3.2. BEÁLLÍTÁSOK / ADATFORRÁSOK (Settings & Sources)

**Cél:** Szilvi (Admin) itt tudja felvenni a "Barna borítékos" ügyfelek fiókjait.

```text
+-----------------------+-------------------------------------------------------+
|  GREKONTO AI          |  ADATFORRÁSOK KEZELÉSE                                |
+-----------------------+-------------------------------------------------------+
|  Műszerfal            |                                                       |
|  Párosítás (12)       |  Itt állíthatod be, honnan gyűjtse az AI a számlákat. |
|  Előzmények           |                                                       |
|  > Beállítások        |  [ + ÚJ FORRÁS HOZZÁADÁSA ]                           |
|                       |                                                       |
|                       |  JELENLEGI FORRÁSOK LISTÁJA:                          |
|                       |  ---------------------------------------------------  |
|                       |  Típus  | Név / Cím             | Ügyfél      | Állapot |
|                       |  -------+-----------------------+-------------+-------|
|                       |  📧 IMAP| kovacs@ceg.hu         | Kovács Bt.  | ✅ OK |
|                       |  📧 IMAP| info@nagyker.hu       | Nagyker Kft.| ⚠️ Err|
|                       |  📂 Drv | /Számlák_2024/        | Grekonto    | ✅ OK |
|                       |  📧 IMAP| szamla@ugyfel.com     | Kis Kft.    | ✅ OK |
|                       |  ---------------------------------------------------  |
|                       |                                                       |
+-----------------------+-------------------------------------------------------+
```

**És ha rákattint az [+ ÚJ FORRÁS] gombra (Modal ablak):**

```text
+-----------------------------------------------------------------------+
|  ÚJ E-MAIL FIÓK BEKÖTÉSE                                     [X] Bezár|
+-----------------------------------------------------------------------+
|                                                                       |
|  Melyik ügyfélhez tartozik?                                           |
|  [ Válassz a partnertörzsből... (Kereshető lista)  v ]                |
|                                                                       |
|  IMAP Szerver beállítások:                                            |
|  Szerver címe: [ imap.gmail.com          ]  Port: [ 993 ] [x] SSL     |
|  Felhasználó:  [ kovacs@ceg.hu           ]                            |
|  Jelszó:       [ *********************** ] (App Password ajánlott!)   |
|                                                                       |
|  [ TESZT KAPCSOLÓDÁS ]  <-- (Gomb megnyomása után zöld pipa, ha jó)   |
|                                                                       |
|                                            [ MENTÉS ÉS FIGYELÉS ]     |
+-----------------------------------------------------------------------+
```

---

### 3.3. ELŐZMÉNYEK ÉS NAPLÓ (Audit Log)

**Cél:** Visszakereshetőség. "Hova lett a tegnapi számla?"

```text
+-----------------------+-------------------------------------------------------+
|  GREKONTO AI          |  FELDOLGOZÁSI NAPLÓ                                   |
+-----------------------+-------------------------------------------------------+
|  Műszerfal            |  [ Szűrő: Minden időszak v ] [ Keresés: Fájlnév...  ] |
|  Párosítás (12)       |                                                       |
|  > Előzmények         |  Időpont   | Fájlnév      | Ügyfél      | Eredmény    |
|  Beállítások          |  ----------+--------------+-------------+-------------|
|                       |  Ma 10:05  | INV_882.pdf  | MVM Next    | ✅ Párosítva|
|                       |            | (Rögzítette: Orbita)                   |
|                       |  ----------+--------------+-------------+-------------|
|                       |  Ma 09:45  | scan002.jpg  | Praktiker   | ⚠️ Kézi     |
|                       |            | (Rögzítette: AI - Bizonytalan)         |
|                       |  ----------+--------------+-------------+-------------|
|                       |  Ma 08:00  | menu.pdf     | -           | 🗑️ Elvetve |
|                       |            | (Ok: Nem számla)                       |
|                       |  ----------+--------------+-------------+-------------|
|                       |  Tegnap    | 2024_sz.pdf  | Kovács Bt.  | ✅ Párosítva|
|                       |            | (Rögzítette: Auto-Match)               |
+-----------------------+-------------------------------------------------------+
```

---

### 3.4. MANUÁLIS FELTÖLTÉS (Upload Zone)

**Cél:** Drag & Drop felület az asszisztensnek a szkennelt anyagokhoz.
Ez megjelenhet egy "Felugró ablakban" (Modal) vagy egy állandó sávban. A Modal jobb választás nagy mennyiségnél.

```text
+-----------------------------------------------------------------------+
|  FÁJLOK FELTÖLTÉSE                                           [X] Bezár|
+-----------------------------------------------------------------------+
|                                                                       |
|          +-------------------------------------------------+          |
|          |                                                 |          |
|          |      ☁️ HÚZD IDE A FÁJLOKAT (Drag & Drop)       |          |
|          |                                                 |          |
|          |            vagy kattints a tallózáshoz          |          |
|          |                                                 |          |
|          +-------------------------------------------------+          |
|                                                                       |
|  Feltöltési lista:                                                    |
|  📄 szamla_maj_01.pdf ........................... [██████████] 100% ✅|
|  📄 szamla_maj_02.pdf ........................... [██████----]  60% ⏳|
|  📷 foto_ebed.jpg ............................... [----------]   0%   |
|                                                                       |
|  Támogatott: PDF, JPG, PNG. (Word, Excel nem támogatott!)             |
|                                                                       |
|                                             [ FELDOLGOZÁS INDÍTÁSA ]  |
+-----------------------------------------------------------------------+
```

**Design irányelvek ezekhez a képernyőkhöz:**

1. **Állapotjelzők:** A listákban (Settings, History) mindig használjunk "Badge"-eket (színes kis címkék: Zöld=OK, Sárga=Figyelem, Piros=Hiba), hogy egy pillantással átlátható legyen a rendszer egészsége.

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-22
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v1.0** (2025-11-22): Eredeti verzió - Teljes UX terv dokumentálva
2. **Validáció:** A Beállítások űrlapnál (3.2) kritikus, hogy a "Mentés" gomb inaktív (szürke) legyen addig, amíg a "Teszt Kapcsolódás" nem volt sikeres. Ne engedjük elmenteni a hibás jelszót!
3. **Empty States:** Ha a lista üres (pl. nincs még előzmény), ne csak üres fehérséget mutassunk, hanem egy kedves ikont és szöveget: *"Még nincs megjeleníthető adat. Kezdj el dolgozni a Műszerfalon!"*

Ezzel a csomaggal a fejlesztők már pixelpontosan tudják építeni a felületeket.
