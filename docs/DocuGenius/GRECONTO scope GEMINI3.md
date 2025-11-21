## Page 1

A megbeszélés alapján az igények (scope) összefoglalása, a résztvevők által
meghatározott csoportosításban és a közösen elfogadott prioritási sorrendben:
1. PRIORITÁS (Proof of Concept / Induló fázis): Adatbegyűjtés és
központosítás
Ez a közösen elfogadott kezdő lépés, mivel ez érinti a legtöbb kollégát és ez a
legkritikusabb "fájdalompont" (a sokféle forrásból érkező dokumentumok kezelése).
• Bemeneti források egységesítése: A rendszernek képesnek kell lennie
automatikusan begyűjteni a bizonylatokat és számlákat különböző csatornákról,
ahol az ügyfelek jelenleg tárolják őket:
– Google Drive
– E-mail csatolmányok
– Dropbox
– Egyéb fájlmegosztók
• Dokumentumok központosítása: A begyűjtött dokumentumok automatikus
eljuttatása a célrendszerbe (AUC System / Audit Cloud).
• Alapadatok kinyerése (Header szint): A számlákról nem a tételes, hanem a fejléc
(header) szintű adatok kinyerése szükséges a könyvelés előkészítéséhez és az
azonosításhoz:
– Számla kelte
– Sorszám
– Szállító neve / Adószáma (Partner azonosítás)
– Végösszeg (Nettó/Bruttó)
– Pénznem
– Speciális jelzések (pl. pénzforgalmi elszámolás, EPR díj, fordított ÁFA
jelzése).
• Formátumkezelés:
– Digitális PDF-ek kezelése.
– Szkennelt (kép alapú) PDF-ek felismerése (OCR).
– Kézírás felismerése nem elvárás (elhanyagolható mennyiség).
• Validálás: Annak felismerése, hogy az adott dokumentum valóban számla-e, vagy
egyéb irreleváns dokumentum/szalvéta fotó.

## Page 2

2. PRIORITÁS: Számlázás automatizálása
Bár eredetileg ez volt az egyik fő igény, a megbeszélés során a második helyre sorolódott
az adatbegyűjtés mögött.
• Excel kiváltása: A jelenlegi manuális, Excel-alapú (keresőfüggvényes) számlázási
előkészítés automatizálása a hibalehetőségek csökkentése érdekében.
• Dinamikus adatkapcsolat: A számlázásnak össze kell kapcsolódnia a
bérszámfejtési adatokkal (pl. hány főt számfejtettek az adott hónapban) és az
ügyfél aktuális státuszával.
• Tömeges számlagenerálás: Feladó tábla automatikus elkészítése a számlázó
program (Számlázz.hu) felé.
3. PRIORITÁS: Ügyfélportál és Ügyfél-történet (History)
Szorosan kapcsolódik a számlázáshoz és az adminisztrációhoz.
• Ügyfél életút követése: Egy felület, ahol visszakereshető az ügyfél története (mikor
mennyi volt a díja, mikor emeltek árat, miért emeltek).
• Szerződéses paraméterek tárolása: Aktív/inaktív státusz, ÁFA kör, riportolási
igények, szerződött szolgáltatások nyilvántartása.
• Automatikus árazási javaslatok (Long-term): A rendszer tegyen javaslatot
áremelésre a historikus adatok alapján.
4. PRIORITÁS: Ad-hoc feladatkezelés és E-mail menedzsment
A megbeszélés alapján ez a "harmadik csomag", a folyamatok menedzsmentje.
• E-mailből feladat: A beérkező e-mailek automatikus kategorizálása (spam,
ügyfélkérés, hatósági levél) és feladattá konvertálása a feladatkezelő rendszerben
(pl. Planner/O365).
• Felelősök hozzárendelése: A feladatok automatikus kiosztása a megfelelő
kollégához.
KIZÁRT vagy KÉSŐBBRE HALASZTOTT elemek (Out of Scope):
• Tételes feldolgozás (Line items): A számlák tételeinek (pl. "citrom" vs. "WC
illatosító") automatikus főkönyvi számra sorolása egyelőre nem cél, ez marad a
könyvelő kompetenciája a második fázisig.
• Munkavégzés profilozása/figyelése: Bár felmerült az igény a folyamatok mérésére
(ki mennyi időt tölt egy ügyféllel), ezt a scope-ból egyelőre kivették, illetve későbbi,
jogilag is tisztázandó lépésnek tekintik.
• Kézírás felismerés: Nem jellemző az üzletmenetre, így nem igény.

## Page 3

Miért ez a prioritás? A megbeszélés konklúziója.
Bár a beszélgetés elején Brigi a számlázást hozta fel "szívügyeként" (mert a
kolléganőknek az fáj), a beszélgetés dinamikája során a szakértők (Valentin és Márk)
javaslatára és a megrendelők (Brigi és Szilvi) beleegyezésével a prioritások
átrendeződtek a megvalósíthatóság és a gyors eredmény érdekében.
Íme a bizonyítékok a szövegből, hogy miért ez a végső scope és prioritás:
1. Miért az adatbegyűjtés lett az 1. prioritás (a PoC tárgya)?
• A javaslat: Valentin mondja ki a döntő érvet: "én azt verziót választanám, hogy az
ügyfél mit hova tölt fel és azt hova kerüljön. Én ezzel nyitnám."
• Az ok: Ez a legkevésbé kockázatos, gyorsan látványos eredményt hoz ("kicsiben
kipróbálható"), és mindenkit érint.
• A jóváhagyás: Brigi és a többiek elfogadják ezt az irányt a beszélgetés végére.
Megállapodnak, hogy erről készül az ajánlat még a héten.
2. Miért került ki a "tételes feldolgozás" (pl. citrom vs. illatosító) a scope-ból?
• A probléma: Brigi hosszan mesél a "citrom" példájáról, hogy a rendszer nem tudja
eldönteni, hogy a citrom alapanyag vagy tisztítószer.
• A döntés: Szilvi mondja ki a végszót: "Szerintem ezt tartsuk meg egy 2. lépésnek."
• A scope szűkítése: Brigi megerősíti, hogy "még abba ne menjünk bele... a
könyvelőnek a feladata, hogy jó ezt eldönti, hogy hova teszi". Tehát a rendszer csak
az adatot adja át (fejléc adatok), a kontírozást (hova könyveljük) nem végzi el
automatán egyelőre.
3. Miért nem foglalkoznak a kézírással?
• Márk felvetette kockázatként, de Brigi egyértelműen kijelentette: "abszolút nem
jellemző... nincsen kézírásos... ez a fehér holló". Ezért ez nem része az igénynek.
4. Mi a helyzet a profilozással (munkavégzés figyelése)?
• Bár Brigi nyitott volt rá ("én nyitott vagyok rá"), Márk jogi aggályokat vetett fel
(GDPR/profilozás), és Brigi is elismerte, hogy "ez már egy külön ez egy külön topik".
Tehát ez nem része a mostani technikai scope-nak.
Összegzés: A leírt scope azért pontos, mert bár igényként minden elhangzott
(számlázás, history, tételes feldolgozás), a szerződéses tárgy (scope) a beszélgetés
végére leszűkült az adatbegyűjtésre és alap-adatkinyerésre, minden mást
tudatosan későbbi fázisra toltak.
