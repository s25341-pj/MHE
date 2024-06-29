import math
import random
import copy
import json
import argparse


########## Czytaj dane z pliku ##########
def wczytajUstawienia(fileName):
    with open(fileName, 'r') as file:
        ustawienia = json.load(file)
    return ustawienia

ustawieniaNonogram = wczytajUstawienia('ustawienia.txt')



########## Implementacja problemu optymalizacyjnego (3) ##########
########## Funkcja celu ##########
def znajdzCiagiJedynek(wierszLubKolumna):
    ciagi = []
    aktualnaDlugosc = 0

    for i in wierszLubKolumna:
        if i == 1:
            aktualnaDlugosc += 1
        elif aktualnaDlugosc > 0:
            ciagi.append(aktualnaDlugosc)
            aktualnaDlugosc = 0

    if aktualnaDlugosc > 0:
        ciagi.append(aktualnaDlugosc)

    return ciagi


def obliczNiezgodnoscZWymaganiami(ciagi, ustawieniaCiagi):
    if isinstance(ustawieniaCiagi, int):
        ustawieniaCiagi = [ustawieniaCiagi]

    niezgodnosc = 0

    roznicaWLiczbieCiagow = abs(len(ciagi) - len(ustawieniaCiagi))
    niezgodnosc += roznicaWLiczbieCiagow * 2

    if len(ciagi) == len(ustawieniaCiagi):
        for rzeczywistaDlugosc, wymaganaDlugosc in zip(ciagi, ustawieniaCiagi):
            niezgodnosc += abs(rzeczywistaDlugosc - wymaganaDlugosc)
    else:
        niezgodnosc += len(ustawieniaCiagi) + 1

    return niezgodnosc

def cel(ustawienia, rozwiazanie):
    sumaNiezgodnosci = 0

    # Analiza wierszy
    for i, wiersz in enumerate(rozwiazanie):
        ciagiJedynek = znajdzCiagiJedynek(wiersz)
        sumaNiezgodnosci += obliczNiezgodnoscZWymaganiami(ciagiJedynek, ustawienia[0][i])

    # Analiza kolumn
    for i in range(len(rozwiazanie[0])):
        kolumna = [rozwiazanie[j][i] for j in range(len(rozwiazanie))]
        ciagiJedynek = znajdzCiagiJedynek(kolumna)
        sumaNiezgodnosci += obliczNiezgodnoscZWymaganiami(ciagiJedynek, ustawienia[1][i])

    return sumaNiezgodnosci


########## Bliskie sąsiedztwo ##########
def bliskieLosoweSasiedztwo(rozwiazanie):
    wierszIndex = random.randrange(len(rozwiazanie))
    kolumnaIndex = random.randrange(len(rozwiazanie[0]))
    rozwiazanie[wierszIndex][kolumnaIndex] = 1 - rozwiazanie[wierszIndex][kolumnaIndex]
    return rozwiazanie


def bliskieSasiedztwo(rozwiazanie, indeksKomorki):
    noweRozwiazanie = [wiersz[:] for wiersz in rozwiazanie]
    kolumnaIndex = math.floor(indeksKomorki / len(rozwiazanie[0]))
    wierszIndex = indeksKomorki % len(rozwiazanie[0])
    noweRozwiazanie[kolumnaIndex][wierszIndex] = 1 - noweRozwiazanie[kolumnaIndex][wierszIndex]
    return noweRozwiazanie


########## Losowe rozwiązanie ##########
def losoweRozwiazanie(ustawienia):
    losweRozwiazanie = [[0 for _ in range(len(ustawienia[1]))] for _ in range(len(ustawienia[0]))]

    for wiersz in range(len(ustawienia[0])):
        for kolumna in range(len(ustawienia[1])):
            losweRozwiazanie[wiersz][kolumna] = random.randrange(0, 100) % 2

    return losweRozwiazanie



########## Algorytm pełnego przeglądu (1) ##########
# Funkcja (brute force) konwertuje liczbę całkowitą na binarny ciąg reprezentujący rozwiązanie w postaci tablicy.
def zamienNaBinarnyCiag(ustawienia, x):
    liczbaWierszy = len(ustawienia[0])
    liczbaKolumn = len(ustawienia[1])
    binarnyCiag = bin(x)[2:].zfill(liczbaWierszy * liczbaKolumn)
    rozwiazanie = []

    for i in range(0, liczbaWierszy * liczbaKolumn, liczbaKolumn):
        wiersz = [int(bit) for bit in binarnyCiag[i:i + liczbaKolumn]]
        rozwiazanie.append(wiersz)

    return rozwiazanie



def zRozwiazaniaNaBinarnyCiag(rozwiazanie):
    binarnyCiag = ''.join(str(bit) for wiersz in rozwiazanie for bit in wiersz)
    return int(binarnyCiag, 2)


# Funkcja przegląda wszystkie możliwe rozwiązania, wybierając najlepsze na podstawie funkcji celu.
def przegladPelny(ustawienia):
    najlepszyCel = float('inf')
    najlepszeRozwiazanie = None
    kwadrat = len(ustawienia[0]) * len(ustawienia[1])
    iloscMozliwosci = 2 ** kwadrat
    for x in range(iloscMozliwosci):
        biezaceRozwiazanie = zamienNaBinarnyCiag(ustawienia, x)
        ocenaBiezacegoRozwiazania = cel(ustawienia, biezaceRozwiazanie)
        print(biezaceRozwiazanie, ocenaBiezacegoRozwiazania)

        if x % 1000000 == 0:
            print(x, "/", iloscMozliwosci)
        if ocenaBiezacegoRozwiazania < najlepszyCel:
            najlepszyCel = ocenaBiezacegoRozwiazania
            najlepszeRozwiazanie = biezaceRozwiazanie
        if najlepszyCel == 0:
            print(x, "/", iloscMozliwosci, " Ocena: ", najlepszyCel, " Rozwiazanie: ", najlepszeRozwiazanie)
            break
    return najlepszeRozwiazanie



########## Algorytm wspinaczkowy (metoda heurystyczna) (1 +1*) ##########
def wspinaczkowyKlasyczny(ustawienia, rozwiazanie):
    najlepszyWynik = cel(ustawienia, rozwiazanie)
    najlepszeRozwiazanie = rozwiazanie
    najlepszaZmiana = None

    while True:
        poprawa = False

        for x in range(len(rozwiazanie[0]) * len(rozwiazanie)):
            noweRozwiazanie = bliskieSasiedztwo(najlepszeRozwiazanie, x)
            wynik = cel(ustawienia, noweRozwiazanie)

            if wynik < najlepszyWynik:
                najlepszyWynik = wynik
                najlepszeRozwiazanie = noweRozwiazanie
                poprawa = True
                najlepszaZmiana = x

            if najlepszyWynik == 0:
                return najlepszeRozwiazanie, najlepszyWynik, najlepszaZmiana

        if not poprawa:
            break

    return najlepszeRozwiazanie, najlepszyWynik, najlepszaZmiana


########## Algorytm tabu (1 + 1*) ##########
# Funkcja implementująca algorytm tabu (optymalizacji) dla rozwiązania nonogramu.
def algorytmTabu(ustawienia, rozwiazaniePoczatkowe, maxDlugoscTabu, liczbaIteracji):
    sasiedzi = []
    listaTabu = []
    stosOdwiedzonych = []

    sprawdzaneRozwiazanie = rozwiazaniePoczatkowe
    najlepszeRozwiazanieGlobalne = rozwiazaniePoczatkowe
    najlepszyWynik = cel(ustawienia, rozwiazaniePoczatkowe)

    if najlepszyWynik == 0:
        return rozwiazaniePoczatkowe

    for i in range(liczbaIteracji):
        if i % 10000 == 0:
            print(i, " : ", liczbaIteracji)

        for x in range(len(rozwiazaniePoczatkowe[0]) * len(rozwiazaniePoczatkowe)):
            if zRozwiazaniaNaBinarnyCiag(bliskieSasiedztwo(sprawdzaneRozwiazanie, x)) not in listaTabu:
                aktualneRozwiazanie = bliskieSasiedztwo(sprawdzaneRozwiazanie, x)
                aktualnyWynik = cel(ustawienia, aktualneRozwiazanie)

                sasiedzi.append([aktualneRozwiazanie, aktualnyWynik])

        if zRozwiazaniaNaBinarnyCiag(sprawdzaneRozwiazanie) not in stosOdwiedzonych and len(sasiedzi) > 0:
            stosOdwiedzonych.append(zRozwiazaniaNaBinarnyCiag(sprawdzaneRozwiazanie))

        if len(sasiedzi) == 0:
            if len(stosOdwiedzonych) != 0:
                sprawdzaneRozwiazanie = zamienNaBinarnyCiag(ustawienia, stosOdwiedzonych[len(stosOdwiedzonych)-1])
                stosOdwiedzonych.pop(len(stosOdwiedzonych)-1)
                sasiedzi.clear()
        else:
            najlepszySasiad = min(sasiedzi, key=lambda x: x[1])
            sprawdzaneRozwiazanie = najlepszySasiad[0]

            if len(listaTabu) >= maxDlugoscTabu:
                listaTabu.pop(0)
            listaTabu.append(zRozwiazaniaNaBinarnyCiag(najlepszySasiad[0]))

            if najlepszySasiad[1] == 0:
                return najlepszySasiad, i

            if najlepszySasiad[1] < najlepszyWynik:
                najlepszyWynik = najlepszySasiad[1]
                najlepszeRozwiazanieGlobalne = najlepszySasiad[0]

            sasiedzi.clear()

    return najlepszeRozwiazanieGlobalne, cel(ustawienia, najlepszeRozwiazanieGlobalne)



########## Algorytm Wyżarzania (1) ##########
# Funkcja implementująca algorytm symulowanego wyżarzania dla rozwiązania nonogramu.
def symulowaneWyzarzanie(ustawienia, poczatkoweRozwiazanie, poczatkowaTemperatura, wspolczynnikSchladzania, minimalnaTemperatura, maksLiczbaIteracji):

    #obecneRozwiazanie = losoweRozwiazanie(ustawienia)

    obecneRozwiazanie = poczatkoweRozwiazanie
    najlepszeRozwiazanie = obecneRozwiazanie
    obecnyCel = cel(ustawienia, obecneRozwiazanie)
    najlepszyCel = obecnyCel
    temperatura = poczatkowaTemperatura

    for i in range(maksLiczbaIteracji):

        if temperatura <= minimalnaTemperatura:
            break

        noweRozwiazanie = bliskieLosoweSasiedztwo(obecneRozwiazanie)
        nowyCel = cel(ustawienia, noweRozwiazanie)

        wskaznikDelta = nowyCel - obecnyCel

        if wskaznikDelta < 0 or random.random() < math.exp(abs(-wskaznikDelta )/ temperatura):
            obecneRozwiazanie = noweRozwiazanie
            obecnyCel = nowyCel
            if nowyCel < najlepszyCel:
                najlepszeRozwiazanie = noweRozwiazanie
                najlepszyCel = nowyCel

        temperatura = poczatkowaTemperatura * (wspolczynnikSchladzania ** i)

    return najlepszeRozwiazanie, najlepszyCel



########## Algorytm Genetyczny (4 + 1*) ##########
# Inicjalizacja populacji
def inicjalizujPopulacje(rozmiarPopulacji, ustawienia):

    populacja = []

    for _ in range(rozmiarPopulacji):
        rozwiazanie = losoweRozwiazanie(ustawienia)
        populacja.append(rozwiazanie)
    return populacja

# Ocena populacji
def ocenaPopulacje(populacja, ustawienia):
    wyniki = []
    for osoba in populacja:
        wynik = cel(ustawienia, osoba)
        wyniki.append((osoba, wynik))
    return wyniki

# Selekcja ruletki
def selekcja(populacja, wyniki, iloscRodzicow):
    wagi = [1 / (wynik + 1e-8) for _, wynik in wyniki]
    wybrani = random.choices(populacja, weights=wagi, k=iloscRodzicow)
    return wybrani

# Krzyżowanie jednopunktowe
def krzyzowanieJednopunktowe(rodzicA, rodzicB):
    punkt = random.randint(1, len(rodzicA) - 1)
    potomekA = rodzicA[:punkt] + rodzicB[punkt:]
    potomekB = rodzicB[:punkt] + rodzicA[punkt:]
    return potomekA, potomekB

# Krzyżowanie dwupunktowe
def krzyzowanieDwupunktowe(rodzicA, rodzicB):
    punktA = random.randint(1, len(rodzicA) - 2)
    punktB = random.randint(punktA + 1, len(rodzicA) - 1)
    potomekA = rodzicA[:punktA] + rodzicB[punktA:punktB] + rodzicA[punktB:]
    potomekB = rodzicB[:punktA] + rodzicA[punktA:punktB] + rodzicB[punktB:]
    return potomekA, potomekB

# Mutacja losowa
def mutacjaLosowa(osoba):
    x = random.randint(0, len(osoba) - 1)
    y = random.randint(0, len(osoba[0]) - 1)
    osoba[x][y] = 1 - osoba[x][y]
    return osoba

# Mutacja swap
def mutacjaSwap(osoba):
    x1, y1 = random.randint(0, len(osoba) - 1), random.randint(0, len(osoba[0]) - 1)
    x2, y2 = random.randint(0, len(osoba) - 1), random.randint(0, len(osoba[0]) - 1)
    osoba[x1][y1], osoba[x2][y2] = osoba[x2][y2], osoba[x1][y1]
    return osoba

# Główna funkcja algorytmu genetycznego
def algorytmGenetyczny(ustawienia, rozmiarPopulacji, iloscPokolen, wspolczynnikKrzyzowania, wspolczynnikMutacji, metodaKrzyzowania, metodaMutacji, warunekZakonczenia, liczbaElitarnych):
    populacja = inicjalizujPopulacje(rozmiarPopulacji, ustawienia)
    najlepszaOsoba = None
    najlepszyWynik = float('inf')


    for pokolenie in range(iloscPokolen):
        wyniki = ocenaPopulacje(populacja, ustawienia)


        for osoba, wynik in wyniki:
            if wynik < najlepszyWynik:
                najlepszyWynik = wynik
                najlepszaOsoba = copy.deepcopy(osoba)

        nowaPopulacja = []


        sortedWyniki = sorted(wyniki, key=lambda x: x[1])
        elitarneOsoby = [copy.deepcopy(osoba) for osoba, _ in sortedWyniki[:liczbaElitarnych]]
        nowaPopulacja.extend(elitarneOsoby)

        while len(nowaPopulacja) < rozmiarPopulacji:
            rodzicA, rodzicB = selekcja(populacja, wyniki, 2)

            if random.random() < wspolczynnikKrzyzowania:
                if metodaKrzyzowania == 'jednopunktowa':
                    potomekA, potomekB = krzyzowanieJednopunktowe(rodzicA, rodzicB)
                elif metodaKrzyzowania == 'dwupunktowa':
                    potomekA, potomekB = krzyzowanieDwupunktowe(rodzicA, rodzicB)
                nowaPopulacja.extend([potomekA, potomekB])
            else:
                nowaPopulacja.extend([rodzicA, rodzicB])

        populacja = nowaPopulacja[:rozmiarPopulacji]

        for i in range(rozmiarPopulacji):
            if random.random() < wspolczynnikMutacji:
                if metodaMutacji == 'mutacjaLosowa':
                    populacja[i] = mutacjaLosowa(copy.deepcopy(populacja[i]))
                elif metodaMutacji == 'mutacjaSwap':
                    populacja[i] = mutacjaSwap(copy.deepcopy(populacja[i]))

        if (warunekZakonczenia == 'liczbaIteracji' and pokolenie >= iloscPokolen - 1):
            print("Program zakończył się z powodu przekroczonej ilości iteracji")
            break
        elif warunekZakonczenia == 'minimalnaWartosc' and najlepszyWynik <= 0:
            print("Program zakończył się z powodu minimalnej wartości")
            break

    return najlepszaOsoba, najlepszyWynik



########## Wczytywanie danych z terminala ##########
def parse_arguments():
    parser = argparse.ArgumentParser(description='Wybór algorytmu do badania')
    subparsers = parser.add_subparsers(dest='algorytm', help='Wybierz algorytm by odpalić')

    # Parser dla celu
    parserCel = subparsers.add_parser('cel')
    parserCel.add_argument('--ustawienia', type=str, default="ustawienia")
    parserCel.add_argument('--plik', type=str, default="plik")
    parserCel.add_argument('--rozwiazanie', type=str, default="losowe")

    # Parser dla sąsiedztwa losowego
    parserSasiedztwoLosowe = subparsers.add_parser('bliskieLosoweSasiedztwo')
    parserSasiedztwoLosowe.add_argument('--rozwiazanie', type=str, default="losowe")

    # Parser dla sąsiedztwa
    parserSasiedztwo = subparsers.add_parser('bliskieSasiedztwo')
    parserSasiedztwo.add_argument('--rozwiazanie', type=str, default="losowe")
    parserSasiedztwo.add_argument('--indeksKomorki', type=int, default=0)

    # Parser dla losowego rozwiązania
    parserLosoweRozwiazanie = subparsers.add_parser('losoweRozwiazanie')
    parserLosoweRozwiazanie.add_argument('--ustawienia', type=str, default="ustawienia")
    parserLosoweRozwiazanie.add_argument('--plik', type=str, default="plik")

    # Parser dla pełnego przeglądu
    parserPrzegladPelny = subparsers.add_parser('przegladPelny')
    parserPrzegladPelny.add_argument('--ustawienia', type=str, default="ustawienia")
    parserPrzegladPelny.add_argument('--plik', type=str, default="plik")

    # Parser dla wspinaczki klasycznej
    parserWspinaczkowyKlasyczny = subparsers.add_parser('wspinaczkowyKlasyczny')
    parserWspinaczkowyKlasyczny.add_argument('--rozwiazanie', type=str, default="losowe")
    parserWspinaczkowyKlasyczny.add_argument('--ustawienia', type=str, default="ustawienia")
    parserWspinaczkowyKlasyczny.add_argument('--plik', type=str, default="plik")

    # Parser dla tablicy tabu
    parserTablicaTabu = subparsers.add_parser('algorytmTabu')
    parserTablicaTabu.add_argument('--rozwiazanie', type=str, default="losowe")
    parserTablicaTabu.add_argument('--ustawienia', type=str, default="ustawienia")
    parserTablicaTabu.add_argument('--plik', type=str, default="plik")
    parserTablicaTabu.add_argument('--maxDlugoscTabu', type=int, default=100)
    parserTablicaTabu.add_argument('--liczbaIteracji', type=int, default=10000)

    # Parser dla symulowane wyzarzanie
    parserSymulowaneWyzarzanie = subparsers.add_parser('symulowaneWyzarzanie')
    parserSymulowaneWyzarzanie.add_argument('--rozwiazanie', type=str, default="losowe")
    parserSymulowaneWyzarzanie.add_argument('--ustawienia', type=str, default="ustawienia")
    parserSymulowaneWyzarzanie.add_argument('--plik', type=str, default="plik")
    parserSymulowaneWyzarzanie.add_argument('--poczatkowaTemperatura', type=float, default=100)
    parserSymulowaneWyzarzanie.add_argument('--wspolczynnikSchladzania', type=float, default=0.95)
    parserSymulowaneWyzarzanie.add_argument('--minimalnaTemperatura', type=float, default=0.01)
    parserSymulowaneWyzarzanie.add_argument('--maksLiczbaIteracji', type=int, default=10000)

    # Parser dla algorytm genetyczny
    parserAlgorytmGenetyczny = subparsers.add_parser('algorytmGenetyczny')
    parserAlgorytmGenetyczny.add_argument('--ustawienia', type=str, default="ustawienia")
    parserAlgorytmGenetyczny.add_argument('--plik', type=str, default="plik")
    parserAlgorytmGenetyczny.add_argument('--rozmiarPopulacji', type=int, default=100)
    parserAlgorytmGenetyczny.add_argument('--iloscPokolen', type=int, default=1000)
    parserAlgorytmGenetyczny.add_argument('--wspolczynnikKrzyzowania', type=float, default=0.9)
    parserAlgorytmGenetyczny.add_argument('--wspolczynnikMutacji', type=float, default=0.1)
    parserAlgorytmGenetyczny.add_argument('--metodaKrzyzowania', type=str, default="jednopunktowa", help='Wybór metody krzyzowania: jednopunktowa/dwupunktowa')
    parserAlgorytmGenetyczny.add_argument('--metodaMutacji', type=str, default="mutacjaLosowa", help='Wybór metody mutacji: mutacjaLosowa/mutacjaSwap')
    parserAlgorytmGenetyczny.add_argument('--warunekZakonczenia', type=str, default="liczbaIteracji", help='Wybór warunku zakonczenia: liczbaIteracji/minimalnaWartosc')
    parserAlgorytmGenetyczny.add_argument('--liczbaElitarnych', type=int, default=0, help='Ilość elity')

    return parser.parse_args()


args = parse_arguments()

if args.algorytm == 'cel':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(ustawienia)
    else:
        rozwiazanie = json.loads(args.rozwiazanie)

    wynik = cel(ustawienia, rozwiazanie)
    print(f'Celem badania jest sprawdzenie poprawności rozwiązania nonogramu.\n'
                 f'Wynik im bliższy 0 tym bardziej poprawny, im dalszy od 0 tym rozwiązanie jest coraz gorsze.\n'
                 f'Obecne rozwiązanie wynosi: {wynik}')

elif args.algorytm == 'bliskieLosoweSasiedztwo':
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(wczytajUstawienia('ustawienia.txt'))
    else:
        rozwiazanie = json.loads(args.rozwiazanie)
    print(bliskieLosoweSasiedztwo(rozwiazanie))

elif args.algorytm == 'bliskieSasiedztwo':
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(wczytajUstawienia('ustawienia.txt'))
    else:
        rozwiazanie = json.loads(args.rozwiazanie)
    indeksKomorki = args.indeksKomorki
    print(bliskieSasiedztwo(rozwiazanie, indeksKomorki))

elif args.algorytm == 'losoweRozwiazanie':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)

    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)

    wynik = losoweRozwiazanie(ustawienia)
    print(wynik)


elif args.algorytm == 'przegladPelny':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)

    wynik = przegladPelny(ustawienia)
    print(wynik)


elif args.algorytm == 'wspinaczkowyKlasyczny':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(ustawienia)
    else:
        rozwiazanie = json.loads(args.rozwiazanie)

    wynik = wspinaczkowyKlasyczny(ustawienia, rozwiazanie)
    print(wynik)

elif args.algorytm == 'algorytmTabu':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(ustawienia)
    else:
        rozwiazanie = json.loads(args.rozwiazanie)

    maxDlugoscTabu = args.maxDlugoscTabu
    liczbaIteracji = args.liczbaIteracji

    wynik = algorytmTabu(ustawieniaNonogram, rozwiazanie, maxDlugoscTabu, liczbaIteracji)
    print(wynik)

elif args.algorytm == 'symulowaneWyzarzanie':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)
    if (args.rozwiazanie == "losowe"):
        rozwiazanie = losoweRozwiazanie(ustawienia)
    else:
        rozwiazanie = json.loads(args.rozwiazanie)

    poczatkowaTemperatura = args.poczatkowaTemperatura
    wspolczynnikSchladzania = args.wspolczynnikSchladzania
    minimalnaTemperatura = args.minimalnaTemperatura
    maksLiczbaIteracji = args.maksLiczbaIteracji

    wynik = symulowaneWyzarzanie(ustawienia, rozwiazanie, poczatkowaTemperatura, wspolczynnikSchladzania, minimalnaTemperatura, maksLiczbaIteracji)
    print(wynik)


elif args.algorytm == 'algorytmGenetyczny':
    if (args.ustawienia == "ustawienia"):
        ustawienia = wczytajUstawienia("ustawienia.txt")
    else:
        ustawienia = json.loads(args.ustawienia)
    if (args.plik != "plik"):
        ustawienia = wczytajUstawienia(args.plik)

    rozmiarPopulacji = args.rozmiarPopulacji
    iloscPokolen = args.iloscPokolen
    wspolczynnikKrzyzowania = args.wspolczynnikKrzyzowania
    wspolczynnikMutacji = args.wspolczynnikMutacji
    metodaKrzyzowania = args.metodaKrzyzowania
    metodaMutacji = args.metodaMutacji
    warunekZakonczenia = args.warunekZakonczenia
    liczbaElitarnych = args.liczbaElitarnych

    najlepszeRozwiazanie, najlepszyWynik = algorytmGenetyczny(ustawienia, rozmiarPopulacji, iloscPokolen, wspolczynnikKrzyzowania, wspolczynnikMutacji, metodaKrzyzowania, metodaMutacji, warunekZakonczenia, liczbaElitarnych)
    print(najlepszeRozwiazanie)

else:
    print("Brak poprawy algorytmu")

# python Nonogram.py cel --ustawienia '[[[1,1,1],[1,1],[4],[2,1],[2,1],[2]],[[2],[1],[3],[1,2],[2,2],[1,2,1]]]' --rozwiazanie '[[0,1,0,0,0,1],[1,1,1,0,1,0],[0,0,1,1,0,0],[1,0,1,0,0,1],[0,0,0,1,1,0],[1,1,0,1,0,1]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt
# python Nonogram.py bliskieLosoweSasiedztwo --rozwiazanie '[[0,1,0,0,0,1],[1,1,1,0,1,0],[0,0,1,1,0,0],[1,0,1,0,0,1],[0,0,0,1,1,0],[1,1,0,1,0,1]]'
# python Nonogram.py bliskieSasiedztwo --rozwiazanie '[[0,1,0,0,0,1],[1,1,1,0,1,0],[0,0,1,1,0,0],[1,0,1,0,0,1],[0,0,0,1,1,0],[1,1,0,1,0,1]]' --indeksKomorki 3
# python Nonogram.py losoweRozwiazanie --ustawienia '[[[1,1,1],[1,1],[4],[2,1],[2,1],[2]],[[2],[1],[3],[1,2],[2,2],[1,2,1]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt
# python Nonogram.py przegladPelny --ustawienia '[[[1,1],[2,1],[3],[1,1]],[[2],[1],[3],[1,2]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt
# python Nonogram.py wspinaczkowyKlasyczny --rozwiazanie '[[0,1,0,0,0,1],[1,1,1,0,1,0],[0,0,1,1,0,0],[1,0,1,0,0,1],[0,0,0,1,1,0],[1,1,0,1,0,1]]' --ustawienia '[[[1,1,1],[1,1],[4],[2,1],[2,1],[2]],[[2],[1],[3],[1,2],[2,2],[1,2,1]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt
# python Nonogram.py algorytmTabu --rozwiazanie '[[0,0,0],[0,1,1],[1,0,0],[0,1,0]]' --ustawienia '[[[1,1],3,1,[1,1]],[[2,1],2,[2,1]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt --maxDlugoscTabu 1000000 --liczbaIteracji 100000
# python Nonogram.py symulowaneWyzarzanie --rozwiazanie '[[0,1,0,0,0,1],[1,1,1,0,1,0],[0,0,1,1,0,0],[1,0,1,0,0,1],[0,0,0,1,1,0],[1,1,0,1,0,1]]' --ustawienia '[[[1,1,1],[1,1],[4],[2,1],[2,1],[2]],[[2],[1],[3],[1,2],[2,2],[1,2,1]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt --poczatkowaTemperatura 100 --wspolczynnikSchladzania 0.99 --minimalnaTemperatura 0.01 --maksLiczbaIteracji 10000
# python Nonogram.py algorytmGenetyczny --ustawienia '[[[1,1,1],[1,1],[4],[2,1],[2,1],[2]],[[2],[1],[3],[1,2],[2,2],[1,2,1]]]' --plik C:\Users\dfeister\Desktop\MHE\ustawienia.txt --rozmiarPopulacji 100 --iloscPokolen 1000 --wspolczynnikKrzyzowania 0.9 --wspolczynnikMutacji 0.1 --metodaKrzyzowania 'jednopunktowa' --metodaMutacji 'mutacjaSwap' --warunekZakonczenia 'liczbaIteracji' --liczbaElitarnych 1
