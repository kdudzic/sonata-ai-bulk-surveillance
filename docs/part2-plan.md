# Drugi etap badań NCN SONATA 19 (ver. 11.08.26)

## Zarys

- W pilocie sprawdzaliśmy, czy model trafnie decyduje o zatrzymaniu pojedynczego wpisu i czy dobrze to uzasadnia - na małej, celowo zbalansowanej próbie. Teraz zmieniamy poziom analizy: w kierunku całego potoku selekcji, działania na populacji, w której przypadki istotne pojawiają się z częstością rzędu jednego na tysiąc lub rzadziej.
- Cel to zbudowanie korpusu kilkunastu tysięcy syntetycznych wpisów przypisanych do syntetycznych autorów i uruchomienie na nim kilka modeli selekcji: listę słów kluczowych, podobieństwo semantyczne, mały klasyfikator trenowany lokalnie i LLM z regułami z pilotażu.
- W korpusie umieścimy 20-40 "łuków narracyjnych" (powiązanych wpisów), w których żaden pojedynczy wpis osobno nie daje podstawy do zatrzymania, a podstawa istnieje tylko przy ich zestawieniu. Każdy selektor uruchomiony zostanie dwukrotnie: widząc jeden (aktualny) wpis albo też aktualny wpis i wcześniejsze wpisy tej samej osoby (czyli serię wypowiedzi tej samej osoby).
- Badania powinny być mniej obciążające dla Dominiki a pełniej wykorzystujące infrastrukturę IT, którą udostępnia nam CSI.

## Pytania badawcze

- Jakie jest znaczenie efektu przyrostowego dla decyzji klasyfikacyjnych przy większej skali zbiorów danych syntetycznych?
- Czy AI pozwala zawęzić zakres gromadzonych danych bez utraty skuteczności? Czy może ten cel jest wewnętrznie sprzeczny: zawężenie na poziomie wpisu może być okupione koniecznością sięgnięcia po historię autora.
- Czy duża różnica wykrywalności pomiędzy opcją "jeden wpis" a opcją "cała historia" mogła by oznaczać, że minimalizacja danych nie prowadzi do redukcji, ale przeniesienia inwazyjności - z szerokości zbioru na głębokość profilu jednostki?

## Dane

- Nowy korpus danych syntetycznych - wpisy z mediów społecznościowych połączone w łuki narracyjne.
- Rząd wielkości: ok. 15 000 wpisów.
- Ok. 20-40 łuków.
- Trzy warstwy:
  - 85%: masa treści zupełnie banalnych.
  - 13%: treści okołozagrożeniowe, które jednak nie uzasadniają retencji - relacje prasowe, cytaty, counterspeech, satyra, gniew bez konkretu
  - 1%: wpisy przypadków celowych.

## Selektory

### Kontrakt

Każdy selektor musi spełniać ten sam kontrakt techniczny:

- **Wejście:** pojedynczy wpis (wariant `POST`) albo wpis + wcześniejsze wpisy tego samego autora (wariant `HISTORY`).
- **Wyjście:** jedna liczba `s` w zakresie `[0,1]` - stopień uzasadnienia retencji dla *badanego wpisu*.
- **Użycie:** sortujemy cały korpus po `s`, tniemy górne 1% / 5% / 20%.

Szczegóły techniczne:

- Jednostką rankingu zostaje wpis, także w wariancie `HISTORY`. Historia jest tylko dodatkowym kontekstem, nie zmienia jednostki analizy. Dzięki temu krzywe z obu wariantów leżą na tej samej osi i różnica między nimi jest bezpośrednio interpretowalna jako "co daje sięgnięcie po głębię profilu".
- Skala nie musi być kalibrowana ani porównywalna *między* selektorami. Odcięcie na stałym budżecie (top 1/5/20%) unieważnia problem kalibracji.

### Rodzaje

#### 1. Selektor leksykalny (ważona lista słów kluczowych).

Lista termów z wagami pogrupowana według kategorii sygnałów z rulebooka (intencja pierwszoosobowa, marker czasowy, wskazanie celu, gotowość/przygotowanie). Score = znormalizowana suma trafień.

Bez progowania sumy trafień. Dwa warianty scoringu:

- Suma wag trafień.
- Liczba **różnych kategorii** sygnałów, które trafiły (bliższe regule decyzyjnej z rulebooka: ">= 2 sygnały umiarkowane").

Plus jako ablacja:

- Regresja logistyczna na TF-IDF, uczona na małym podzbiorze z etykietami - daje kalibrowane 0-1. Współczynniki to *automatycznie wyprowadzona* lista słów kluczowych.

Przy wariancie z historią definiujemy jawnie regułę agregacji, np. `s = a * score(wpis) + (1-a) * max/mean score(historia)` albo liczba różnych kategorii sygnałów trafionych w całym oknie.

#### 2. Selektor semantyczny (encoder-only + sonda liniowa).

Podobieństwo do konkretnego zbioru odniesienia:

- **2a. Zero-shot (kotwice).** Embedujemy wpis i liczymy cosinusowe podobieństwo do małego zbioru kotwic: krótkich opisów sygnałów z rulebooka. Score = max albo średnia po kotwicach. Wynik będzie silnie zależny od doboru kotwic.
- **2b. Sonda uczona.** Zamrożony enkoder, na embeddingach uczymy regresję logistyczną na podzbiorze z etykietami.

Wariant `HISTORY`: uśredniony embedding historii doklejony do embeddingu wpisu (konkatenacja wektorów), oraz konkatenacja tekstów - 2 podejścia.

### Do rozważenia

- Czy znalazłyby się inne racjonalne podejścia do 2a?
- Czy istnieje metoda pozwalająca na odtworzenie wartswy tekstowej z embeddingu? Wtedy potencjalne argumenty do przechowywania tylko embeddingów byłyby słabsze.

#### 3. LLM z regułami z pilotażu.

Wiadomo.

### Do rozważenia

- Modele encoder-only mają małe okno kontekstu. Z pełną historią może dałby radę np. ModernBERT? Czy są inne?
- Jaką mamy heurystykę doboru modeli? Chcemy wykorzystać infrastrukturę CSI, więc powinniśmy sprawdzać modele OS. Ale czy to ma być porównanie closed-source z OS? Same OS? Czy robimy jakieś kontrasty chińskie-nie chińskie? Np. pojedyncza alteracja korpusu z treściami anty-chińskimi? Czy modele chińskie będą działać znacznie gorzej? Wstępnie: kilka modeli w pilocie, jeden później.
- Etykietowanie podzbioru pod selektor 2b: ile wpisów wystarczy? Przy 1% pozytywów sonda potrzebuje kilkuset pozytywów, żeby cokolwiek złapać. Może wymagać oversamplingu przy uczeniu albo doetykietowania.

## Metody

### Generacja danych

- Przypadki celowe robimy ręcznie (dla korpusu 15 000 wpisów to będzie ledwo ~150 wpisów). Możemy je nawet wziąć żywcem z jakichś serwisów lub istniejącego korpusu. Potrzebny byłby wtedy check poziomu kontaminacji - reguła do przemyślenia, np. "zidentyfikuj autora wpisu / datę napisania".

- Generowanie syntetycznych wpisów okazało się nie takie łatwe. Powinniśmy do tego podejść bardziej metodologicznie. Spróbowałbym tutaj np. wykorzystania techniki *verbalized sampling* [(link)](https://arxiv.org/abs/2510.01171). Uniwersalnie dobrze działająca metoda generacji syntetycznych wpisów z mediów społecznościowych z jakąś dozą "podejrzaności" mniej lub bardziej uzasadniającą retencję byłaby wkładem naukowym sama w sobie.

- Trzeba nadać autorom stabilną tożsamość stylistyczną i oś czasu. To wydaje mi się dosyć proste. Albo od razu generujemy całą historię wpisów dla pojedynczego autora zgodnie z wytycznymi, albo robimy first pass z generacją pojedynczych wpisów i second pass, gdzie model generujący rozwija nam wpisy do długości całej historii wpisów.

### Do rozważenia

- Czy będą gotowe zbiory, które można by wykorzystać? Jeśli tak, to trzeba będzie też sprawdzić poziom kontaminacji.

### Ewaluacja

Żaden selektor nie decyduje binarnie. każdy szereguje cały korpus według stopnia uzasadnienia retencji, a my odcinamy górne 1%, 5% i 20%. Porównujemy więc architektury przy równym poziomie ingerencji i dostajemy krzywe: wykrywalności oraz inwazyjności, mierzonej liczbą osób niepowiązanych z niczym, a których dane zostały zatrzymane (czyli mamy wskaźnik, ile trzeba zgromadzić danych niepotrzebnych, aby wykryć jeden potrzebny).

## Kamienie milowe

### Faza 1: projekt

**M1 - decyzje projektowe.** Za 2 tygodnie

- Definicja skali i reguły agregacji dla wariantu `HISTORY`.
- Zestaw metryk.
- Protokół antykontaminacyjny na papierze.
- Rozmiar korpusu docelowego.

**M2 - pipeline generacji.** Za 4 tygodnie

- Implementacja verbalized sampling.
- Generacja tożsamości autorów i osi czasu.
- Próbka 200 wpisów.
- Ręczny przegląd jakości - czy wpisy nie są zbyt jednorodne.

### Faza 2: szkielet

**M3 - korpus szkieletowy.** Za 6 tygodni

- 4000 wpisów, 200 autorów, 10 łuków. Przypadki celowe napisane ręcznie.
- Gold labels dla wszystkich przypadków celowych i dla próbki warstwy okołozagrożeniowej.

**M4 - selektory 1-2.** Za 9 tygodni

- Selektor leksykalny.
- Selektor semantyczny.
- Pierwsze krzywe wykrywalności i inwazyjności.

**M5 - Selektor LLM + pełne porównanie na szkielecie.** Za 12 tygodni

- Wszystkie trzy selektory razy dwa warianty.
- Ocena kształtu krzywych.
- Decyzja: skalujemy do 15 000 wpisów, zostajemy przy kilku tysiącach, czy przeprojektowujemy korpus.

### Faza 3: skala

**M6 - korpus docelowy.** Za 17 tygodni

- Pełna skala według decyzji z wcześniej. Trzy warstwy w zadanych proporcjach. 20-40 łuków.
- Kontrola kontaminacji na przypadkach celowych.

**M7 - pełny przebieg ewaluacyjny.** Za 21 tygodni

- Osiem przebiegów na pełnym korpusie.
- Krzywe przy odcięciach 1% / 5% / 20%.
- Wskaźnik inwazyjności: ilu niepowiązanych autorów zatrzymano na jeden wykryty przypadek.

### Faza 4: analiza i pisanie

**M8 - testy kontrolne.** Za 25 tygodni

- Test biasu, wzorowany na pilotażu.
- Kontrola wspólnej listy cech generatora i selektora.
- Ablacje: lista ręczna kontra regresja logistyczna, kotwice kontra sonda uczona.

**M9 - analiza jakościowa.** Za 28 tygodni

- Przypadki brzegowe. Które łuki złapał wyłącznie wariant `HISTORY`. Gdzie tańsze architektury przegrywają, a gdzie nie.

**M10 - draft artykułu.** Za 32 tygodnie

- Pełny szkic z wykresami.
