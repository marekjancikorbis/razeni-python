# -*- coding: utf-8 -*-
"""
Čtyři třídící algoritmy: bubble sort, selection sort, quick sort, merge sort.
K tomu okno v tkinteru, ve kterém se dá řazení sledovat krok za krokem.

Všechny funkce řadí čísla od nejmenšího po největší. Původní seznam
nechávají být, vždycky vrátí nový seřazený seznam (na začátku si z něj
udělám kopii). Díky tomu se dá snadno porovnat výsledek s vestavěným sorted().

Každá funkce má ještě nepovinný parametr "krok". Je to funkce, kterou
algoritmus zavolá po každém kroku (porovnání, prohození...), aby ji
grafické okno mohlo zaznamenat a vykreslit. Pro samotné řazení se
nepoužívá, takže když se ho nezadá, algoritmus běží normálně dál.

Čas řazení měří funkce zmer_cas(). Okno ho ukazuje pod grafem a výpis
z "python razeni.py --test" ho má u každého algoritmu na ukázkovém seznamu.

Rychlý přehled (n = počet prvků):

    algoritmus       nejlepší     průměr       nejhorší     paměť      stabilní
    bubble sort      O(n)         O(n^2)       O(n^2)       O(1)       ano
    selection sort   O(n^2)       O(n^2)       O(n^2)       O(1)       ne
    quick sort       O(n log n)   O(n log n)   O(n^2)       O(log n)   ne
    merge sort       O(n log n)   O(n log n)   O(n log n)   O(n)       ano

Stabilní znamená, že dva stejné prvky zůstanou ve stejném pořadí, v jakém
byly na začátku. U čísel je to jedno, ale u třídění např. lidí podle věku
už na tom záleží.

Spuštění:
    python razeni.py           otevře okno s vizualizací
    python razeni.py --test    jen zkontroluje, že všechny algoritmy řadí správně

V okně jde čísla načíst i z textového souboru (tlačítko "Načíst ze souboru…").
"""

import os
import random
import re
import sys
import tempfile
import time
import tkinter as tk
from collections import namedtuple
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# 1) BUBBLE SORT (bublinkové řazení)
# ---------------------------------------------------------------------------
def bubble_sort(vstup, krok=None):
    """
    Princip:
        Procházím seznam zleva doprava a pořád porovnávám dva sousední
        prvky. Když je levý větší než pravý, tak je prohodím. Tím se největší
        číslo během jednoho průchodu "probublá" až úplně na konec, stejně
        jako bublinka ve vodě stoupá nahoru. Po prvním průchodu je tedy na
        posledním místě to nejvyšší číslo, po druhém průchodu druhé nejvyšší
        na předposledním místě atd. Po n-1 průchodech je všechno seřazené.

    Dvě drobná vylepšení, která mám v kódu:
        - po každém průchodu je poslední (neseřazený) prvek už na svém místě,
          takže další průchod může být o jedno porovnání kratší,
        - když v celém průchodu nedojde k jedinému prohození, je seznam
          seřazený a můžu skončit dřív (u už seřazeného seznamu stačí
          jeden průchod, proto je nejlepší případ O(n)).
    """
    data = list(vstup)          # pracuju s kopií, ať neničím vstup
    n = len(data)

    for kolo in range(n - 1):   # maximálně n-1 průchodů
        prohodil = False        # zatím jsem v tomhle kole nic neprohodil

        # Za posledních "kolo" prvků už je to seřazené, tak tam nelezu.
        # Proto končím o "kolo" dřív. Porovnávám dvojice (j, j+1).
        for j in range(n - 1 - kolo):
            if krok:  # jen pro okno, na řazení nemá vliv
                krok(data, f"Porovnávám {data[j]} a {data[j + 1]}", "porovnani",
                     {j: "porov", j + 1: "porov"})

            if data[j] > data[j + 1]:
                # sousedi jsou ve špatném pořadí, tak je prohodím
                data[j], data[j + 1] = data[j + 1], data[j]
                prohodil = True
                if krok:
                    krok(data, f"Prohozeno, {data[j + 1]} > {data[j]}", "prohozeni",
                         {j: "prohoz", j + 1: "prohoz"})

        if krok:
            krok(data, f"Konec {kolo + 1}. průchodu, {data[n - 1 - kolo]} je na svém místě",
                 "info", {n - 1 - kolo: "hotovo"})

        if not prohodil:
            # celé kolo bez jediného prohození = vše je už v pořádku
            break

    return data


# ---------------------------------------------------------------------------
# 2) SELECTION SORT (řazení výběrem)
# ---------------------------------------------------------------------------
def selection_sort(vstup, krok=None):
    """
    Princip:
        Seznam si představuju rozdělený na dvě části. Vlevo je seřazená část
        (na začátku prázdná), vpravo zbytek, který ještě seřazený není.
        V pravé části najdu nejmenší prvek a prohodím ho s prvním prvkem
        téhle části. Hranice mezi částmi se tím posune o jedno místo
        doprava. Opakuju, dokud v neseřazené části něco zbývá.

    Oproti bubble sortu se tu moc neprohazuje (maximálně n-1 prohození),
    ale porovnává se pořád stejně moc, i kdyby už bylo vše seřazené. Proto
    je to vždycky O(n^2). Nestabilní je kvůli tomu, že prohození může
    přeskočit přes stejný prvek, např. [2a, 2b, 1] -> [1, 2b, 2a].
    """
    data = list(vstup)
    n = len(data)

    # i = první místo neseřazené části (vlevo od i je hotovo)
    # Stačí jít do n-2, poslední prvek už pak musí sedět sám od sebe.
    for i in range(n - 1):
        index_min = i               # zatím tipuju, že nejmenší je hned první

        # projdu zbytek a hledám, jestli tam není něco menšího
        for j in range(i + 1, n):
            if krok:
                krok(data, f"Hledám minimum: porovnávám {data[j]} s dosavadním minimem {data[index_min]}",
                     "porovnani", {i: "start", index_min: "min", j: "porov"})

            if data[j] < data[index_min]:
                index_min = j       # pamatuju si pozici, ne hodnotu

        # nejmenší prvek dám na pozici i (když tam už není)
        if index_min != i:
            data[i], data[index_min] = data[index_min], data[i]
            if krok:
                krok(data, f"Minimum {data[i]} jde na místo {i}", "prohozeni",
                     {i: "hotovo", index_min: "prohoz"})
        elif krok:
            krok(data, f"Minimum {data[i]} už je na svém místě", "info", {i: "hotovo"})

    return data


# ---------------------------------------------------------------------------
# 3) QUICK SORT (rychlé řazení)
# ---------------------------------------------------------------------------
def quick_sort(vstup, krok=None):
    """
    Princip (rozděl a panuj):
        Vyberu jeden prvek, kterému se říká pivot. Pak seznam přerovnám tak,
        aby všechno menší než pivot bylo vlevo od něj a všechno ostatní
        vpravo. Pivot tím skončí na svém konečném místě, to už se nikdy
        nezmění. Levou a pravou část pak řadím úplně stejným způsobem
        (rekurzivně) a to se opakuje, dokud nemají části jen jeden prvek
        nebo žádný. Na konci není co slučovat, protože se řadí přímo
        v tom samém seznamu.

    Rychlost záleží na tom, jak vyvážené rozdělení vyjde. Když pivot
    rozdělí seznam zhruba napůl, je hloubka rekurze asi log2(n) a v každé
    hloubce se celkem projde n prvků, tedy O(n log n). Když ale pivot
    pokaždé vyjde jako nejmenší nebo největší prvek, je to O(n^2).
    Pivot proto beru z prostředka, tím se vyhnu nejhoršímu případu u už
    seřazených seznamů.

    Poznámka: když je v seznamu spousta stejných hodnot, rozdělení vychází
    nerovnoměrně a program zpomalí. A u opravdu dlouhých takových seznamů
    (tisíce stejných čísel) by mohl narazit na limit rekurze v Pythonu.
    """
    data = list(vstup)
    _quick_sort_rekurze(data, 0, len(data) - 1, krok)
    return data


def _quick_sort_rekurze(data, zacatek, konec, krok):
    """Seřadí úsek data[zacatek..konec] (včetně obou krajů) přímo v seznamu."""
    # Úsek s 0 nebo 1 prvkem je seřazený sám od sebe, tady rekurze končí.
    if zacatek >= konec:
        if krok and zacatek == konec:
            krok(data, f"Úsek s jedním prvkem ({data[zacatek]}) je hotový", "info", {zacatek: "hotovo"})
        return

    # rozdělení vrátí, na jakém indexu skončil pivot
    pozice_pivota = _rozdel(data, zacatek, konec, krok)

    # pivot už je na správném místě, řadím jen to, co je vlevo a vpravo od něj
    _quick_sort_rekurze(data, zacatek, pozice_pivota - 1, krok)
    _quick_sort_rekurze(data, pozice_pivota + 1, konec, krok)


def _rozdel(data, zacatek, konec, krok):
    """
    Rozdělení (partition) úseku kolem pivota.

    Postup:
        1. pivot vezmu z prostředka a prohodím ho s posledním prvkem,
           ať mi nepřekáží, když budu procházet zbytek,
        2. proměnná "hranice" ukazuje na první místo, kde už jsou
           prvky >= pivot (na začátku je to hned začátek úseku),
        3. projdu všechny ostatní prvky, a když je nějaký menší než pivot,
           prohodím ho s prvkem na hranici a hranici posunu o jedno doprava.
           Tím se menší prvky hromadí na levé straně,
        4. nakonec pivot z konce prohodím na hranici. Vlevo jsou pak
           samé menší prvky a vpravo samé větší nebo stejné.
    """
    stred = (zacatek + konec) // 2
    if krok:
        krok(data, f"Pivot je prostřední prvek: {data[stred]}", "info", {stred: "pivot"})
    data[stred], data[konec] = data[konec], data[stred]
    pivot = data[konec]
    if krok and stred != konec:
        krok(data, "Pivot dávám na konec úseku", "prohozeni", {konec: "pivot", stred: "prohoz"})

    hranice = zacatek
    for i in range(zacatek, konec):
        if krok:
            krok(data, f"Je {data[i]} menší než pivot {pivot}?", "porovnani",
                 {konec: "pivot", hranice: "hranice", i: "porov"})

        if data[i] < pivot:
            data[i], data[hranice] = data[hranice], data[i]
            if krok and i != hranice:
                krok(data, f"{data[hranice]} je menší, jde k hranici", "prohozeni",
                     {konec: "pivot", hranice: "prohoz", i: "prohoz"})
            hranice += 1

    # pivot jde z posledního místa na hranici, kam doopravdy patří
    data[hranice], data[konec] = data[konec], data[hranice]
    if krok:
        krok(data, f"Pivot {pivot} jde na hranici a je na svém místě",
             "prohozeni" if hranice != konec else "info", {konec: "prohoz", hranice: "hotovo"})
    return hranice


# ---------------------------------------------------------------------------
# 4) MERGE SORT (řazení slučováním)
# ---------------------------------------------------------------------------
def merge_sort(vstup, krok=None):
    """
    Princip (rozděl a panuj):
        Seznam rozpůlím, každou půlku seřadím (zase stejným způsobem, tedy
        rekurzivně) a pak dvě seřazené půlky sloučím do jedné seřazené.
        Půlení pokračuje, dokud nezbydou úseky o jednom prvku, a ty jsou
        seřazené automaticky. Celá práce se tedy děje až při slévání na
        cestě zpátky.

    Rychlost:
        Půlit se dá asi log2(n)-krát a slévání na každé úrovni projde
        dohromady n prvků. Vychází O(n log n) vždycky, bez ohledu na to, jak
        vypadají vstupní data. Cena za to je extra paměť O(n) na pomocné
        seznamy při slévání.
    """
    data = list(vstup)
    _merge_sort_rekurze(data, 0, len(data), krok)
    return data


def _merge_sort_rekurze(data, zacatek, konec, krok):
    """Seřadí úsek data[zacatek:konec] (konec už do úseku nepatří)."""
    # úsek o 0 nebo 1 prvku je seřazený, není co dělat
    if konec - zacatek <= 1:
        return

    stred = (zacatek + konec) // 2
    _merge_sort_rekurze(data, zacatek, stred, krok)   # seřadím levou půlku
    _merge_sort_rekurze(data, stred, konec, krok)     # seřadím pravou půlku
    _slij(data, zacatek, stred, konec, krok)          # a sloučím je dohromady


def _slij(data, zacatek, stred, konec, krok):
    """
    Sloučí dva už seřazené úseky data[zacatek:stred] a data[stred:konec]
    do jednoho seřazeného úseku.

    Postup: u každého úseku si držím ukazatel na první nepoužitý prvek.
    V každém kroku porovnám ty dva prvky, menší přesunu do výsledku
    a ukazatel toho úseku posunu dál. Nemusím porovnávat nic jiného,
    protože v obou úsecích jsou nejmenší prvky vždy vpředu. Když jeden
    úsek dojde, zbytek druhého jen přilepím na konec (je taky seřazený).
    """
    leva = data[zacatek:stred]      # kopie levé půlky
    prava = data[stred:konec]       # kopie pravé půlky
    vysledek = []
    i = 0   # ukazatel do levé půlky
    j = 0   # ukazatel do pravé půlky

    def pohled():
        # jen pro okno: jak by teď celý seznam vypadal (hotová část + to, co zbývá)
        return data[:zacatek] + vysledek + leva[i:] + prava[j:] + data[konec:]

    while i < len(leva) and j < len(prava):
        if krok:
            a = zacatek + len(vysledek)     # tady teď leží první nepoužitý prvek levé půlky
            b = a + len(leva) - i           # a tady pravé půlky
            barvy = {k: "segment" for k in range(zacatek, konec)}
            barvy.update({a: "porov", b: "porov"})
            krok(pohled(), f"Porovnávám {leva[i]} a {prava[j]} (slévání úseku {zacatek + 1} až {konec})",
                 "porovnani", barvy)

        # Při rovnosti beru z levé půlky. Díky tomu zůstanou stejné
        # prvky ve svém původním pořadí a algoritmus je stabilní.
        if leva[i] <= prava[j]:
            vysledek.append(leva[i])
            i += 1
        else:
            vysledek.append(prava[j])
            j += 1

        if krok:
            barvy = {k: "segment" for k in range(zacatek, konec)}
            barvy[zacatek + len(vysledek) - 1] = "prohoz"
            krok(pohled(), f"Do výsledku jde {vysledek[-1]}", "prohozeni", barvy)

    # jeden úsek je vyčerpaný, druhý má zbytek, který už jen přidám
    zbylo = len(leva) - i + len(prava) - j
    vysledek.extend(leva[i:])
    vysledek.extend(prava[j:])
    data[zacatek:konec] = vysledek

    if krok:
        krok(data, f"Zbytek ({zbylo}) se jen přidá na konec, úsek {zacatek + 1} až {konec} je slitý",
             "prohozeni", {k: "segment" for k in range(zacatek, konec)}, zbylo)


# ---------------------------------------------------------------------------
# Měření času
# ---------------------------------------------------------------------------
def zmer_cas(algoritmus, vstup):
    """
    Změří, jak dlouho algoritmus řadí daný seznam (v sekundách).

    Měří se čisté řazení, bez parametru "krok", takže do času se nepočítá
    ani zapisování kroků pro okno, ani vykreslování. U krátkých seznamů trvá
    jedno řazení jen pár mikrosekund a takhle krátký čas by hodiny neměřily
    přesně. Proto algoritmus spustím víckrát za sebou (pokaždé desetkrát
    víc, dokud to celé netrvá aspoň 0,02 s) a celkový čas vydělím počtem
    spuštění.
    """
    opakovani = 1
    while True:
        zacatek = time.perf_counter()
        for _ in range(opakovani):
            algoritmus(vstup)
        celkem = time.perf_counter() - zacatek
        if celkem >= 0.02 or opakovani >= 1_000_000:
            return celkem / opakovani
        opakovani *= 10


def format_casu(sekundy):
    """Čas v rozumných jednotkách s desetinnou čárkou, třeba '12,3 µs' nebo '4,56 ms'."""
    if sekundy < 1e-3:
        text = f"{sekundy * 1e6:.1f} µs"
    elif sekundy < 1:
        text = f"{sekundy * 1e3:.2f} ms"
    else:
        text = f"{sekundy:.2f} s"
    return text.replace(".", ",")


# ---------------------------------------------------------------------------
# Načtení dat ze souboru
# ---------------------------------------------------------------------------
def nacti_soubor(cesta):
    """
    Načte celá čísla z textového souboru (.txt). Čísla můžou být oddělená
    mezerou, čárkou, středníkem nebo novým řádkem. Když v souboru je něco,
    co není celé číslo, vyhodí ValueError.
    """
    # utf-8-sig, aby nevadil BOM, který tam dává Poznámkový blok
    with open(cesta, encoding="utf-8-sig") as soubor:
        casti = [c for c in re.split(r"[,;\s]+", soubor.read()) if c]
    cisla = []
    for c in casti:
        try:
            cisla.append(int(c))
        except ValueError:
            raise ValueError(f"'{c}' není celé číslo") from None
    return cisla


# ---------------------------------------------------------------------------
# Záznam kroků (aby se dalo přehrávat i couvat)
# ---------------------------------------------------------------------------
# Jeden snímek = stav seznamu po jednom kroku + co se právě děje
Snimek = namedtuple("Snimek", "stav text barvy hotovo porovnani prohozeni")


def nahraj_snimky(algoritmus, vstup):
    """Spustí algoritmus a zapíše si každý jeho krok do seznamu snímků."""
    snimky = []
    hotovo = set()          # indexy, které už jsou na konečném místě
    pocty = [0, 0]          # kolik bylo zatím porovnání a prohození

    def zapis(stav, text, typ, barvy, pocet=1):
        hotovo.update(i for i, role in barvy.items() if role == "hotovo")
        if typ == "porovnani":
            pocty[0] += pocet
        elif typ == "prohozeni":
            pocty[1] += pocet
        snimky.append(Snimek(list(stav), text, dict(barvy), frozenset(hotovo), pocty[0], pocty[1]))

    zapis(vstup, "Výchozí seznam", "info", {})
    vysledek = algoritmus(vstup, krok=zapis)
    zapis(vysledek, "Hotovo, seznam je seřazený", "info", {i: "hotovo" for i in range(len(vysledek))})
    return snimky


# ---------------------------------------------------------------------------
# Grafické okno (tkinter)
# ---------------------------------------------------------------------------
ALGORITMY = {
    "Bubble sort": bubble_sort,
    "Selection sort": selection_sort,
    "Quick sort": quick_sort,
    "Merge sort": merge_sort,
}

# co vypíšu do textového pole dole v okně
POPISY = {
    "Bubble sort": (
        "Porovnává dva sousední prvky a když jsou ve špatném pořadí, prohodí je. "
        "Největší číslo tak při jednom průchodu doputuje na konec. Po každém průchodu je "
        "o jeden prvek víc na svém místě. Když se v celém průchodu nic neprohodí, je hotovo.",
        "nejlepší O(n), průměrně i nejhůř O(n²), paměť O(1), stabilní",
    ),
    "Selection sort": (
        "V neseřazené části najde nejmenší prvek a prohodí ho s jejím prvním prvkem. "
        "Seřazená část vlevo se tak po každém kroku zvětší o jeden prvek. "
        "Prohazuje se málo (nejvýš n−1 krát), ale porovnává se pořád stejně.",
        "vždy O(n²), paměť O(1), nestabilní",
    ),
    "Quick sort": (
        "Vybere pivot (prostřední prvek) a ostatní rozdělí na menší (vlevo) a větší nebo stejné "
        "(vpravo). Pivot pak stojí na svém konečném místě. Stejným způsobem se seřadí obě části. "
        "Řadí se přímo v seznamu, nic se neslučuje.",
        "průměrně O(n log n), nejhůř O(n²), paměť O(log n), nestabilní",
    ),
    "Merge sort": (
        "Úsek rozpůlí, obě půlky seřadí a sloučí. Při slévání se porovnávají první nepoužité "
        "prvky obou půlek a menší se přesune do výsledku. Při rovnosti se bere z levé půlky, "
        "proto je řazení stabilní.",
        "vždy O(n log n), paměť O(n), stabilní",
    ),
}

BARVY = {
    "obycejny": "#cfd8dc",   # nic se s ním neděje
    "porov": "#1976d2",      # právě porovnávané prvky
    "prohoz": "#fb8c00",     # právě prohozené nebo přesunuté prvky
    "hotovo": "#43a047",     # už na konečném místě
    "pivot": "#8e24aa",      # pivot u quick sortu
    "hranice": "#fbc02d",    # hranice u quick sortu
    "min": "#e53935",        # dosavadní minimum u selection sortu
    "start": "#fff176",      # začátek neseřazené části u selection sortu
    "segment": "#b3e5fc",    # úsek, který se zrovna slévá u merge sortu
}

# které barvy se v legendě ukážou u kterého algoritmu
LEGENDA = {
    "Bubble sort": [("porov", "porovnávané"), ("prohoz", "prohozené"), ("hotovo", "na svém místě")],
    "Selection sort": [("start", "začátek neseřazené části"), ("min", "dosavadní minimum"),
                       ("porov", "porovnávaný"), ("prohoz", "prohozený"), ("hotovo", "na svém místě")],
    "Quick sort": [("pivot", "pivot"), ("hranice", "hranice"), ("porov", "porovnávaný"),
                   ("prohoz", "prohozené"), ("hotovo", "na svém místě")],
    "Merge sort": [("segment", "slévaný úsek"), ("porov", "porovnávané"), ("prohoz", "přesunutý do výsledku"),
                   ("hotovo", "hotovo")],
}

MIN_PRVKU = 2
MAX_PRVKU = 60


class Okno(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Třídící algoritmy")
        self.geometry("1080x740")
        self.minsize(860, 620)

        self.data = []
        self.snimky = []
        self.cas = 0.0           # za jak dlouho vybraný algoritmus seřadí aktuální seznam
        self.poloha = 0          # který snímek se zrovna ukazuje
        self.bezi = False
        self.uloha = None        # id naplánovaného kroku přehrávání (kvůli zrušení)
        self._nastavuji = False  # aby posuvník nevolal sám sebe

        self._postav()
        self._nova_data()

        self.bind("<space>", lambda e: self._klavesa(self.prepni))
        self.bind("<Right>", lambda e: self._klavesa(lambda: self.o_krok(1)))
        self.bind("<Left>", lambda e: self._klavesa(lambda: self.o_krok(-1)))
        self.bind("<Home>", lambda e: self._klavesa(lambda: self.jdi_na(0)))
        self.bind("<End>", lambda e: self._klavesa(lambda: self.jdi_na(len(self.snimky) - 1)))
        self.protocol("WM_DELETE_WINDOW", self._zavri)

    # ---------------------------------------------------------------- stavba okna
    def _postav(self):
        hlavni = ttk.Frame(self, padding=10)
        hlavni.pack(fill="both", expand=True)

        # horní panel: výběr algoritmu a dat
        horni = ttk.Frame(hlavni)
        horni.pack(fill="x")

        ttk.Label(horni, text="Algoritmus:").pack(side="left")
        self.vyber = ttk.Combobox(horni, values=list(ALGORITMY), state="readonly", width=15)
        self.vyber.current(0)
        self.vyber.pack(side="left", padx=(5, 15))
        self.vyber.bind("<<ComboboxSelected>>", lambda e: self._zmena_algoritmu())

        ttk.Label(horni, text="Počet prvků:").pack(side="left")
        self.pocet = tk.IntVar(value=14)
        pole = ttk.Spinbox(horni, from_=MIN_PRVKU, to=MAX_PRVKU, width=4, textvariable=self.pocet,
                           command=self._nova_data)
        pole.pack(side="left", padx=(5, 8))
        pole.bind("<Return>", lambda e: self._nova_data())
        ttk.Button(horni, text="Zamíchat", command=self._nova_data).pack(side="left", padx=(0, 20))

        ttk.Label(horni, text="Vlastní čísla:").pack(side="left")
        self.vlastni = ttk.Entry(horni, width=30)
        self.vlastni.pack(side="left", padx=5)
        self.vlastni.bind("<Return>", lambda e: self._pouzij_vlastni())
        ttk.Button(horni, text="Použít", command=self._pouzij_vlastni).pack(side="left")
        ttk.Button(horni, text="Načíst ze souboru…", command=self._nacti_ze_souboru).pack(side="left", padx=(5, 0))

        # plátno se sloupci
        self.platno = tk.Canvas(hlavni, bg="white", highlightthickness=1, highlightbackground="#b0bec5",
                                height=360)
        self.platno.pack(fill="both", expand=True, pady=(10, 6))
        self.platno.bind("<Configure>", lambda e: self._vykresli())

        # popis aktuálního kroku a počítadla
        self.popis_kroku = ttk.Label(hlavni, text="", font=("Segoe UI", 12, "bold"), anchor="w")
        self.popis_kroku.pack(fill="x")
        self.pocitadla = ttk.Label(hlavni, text="", foreground="#455a64", anchor="w")
        self.pocitadla.pack(fill="x", pady=(0, 6))

        # ovládání přehrávání
        ovladani = ttk.Frame(hlavni)
        ovladani.pack(fill="x")
        ttk.Button(ovladani, text="⏮", width=4, command=lambda: self.jdi_na(0)).pack(side="left")
        ttk.Button(ovladani, text="◀ Zpět", width=9, command=lambda: self.o_krok(-1)).pack(side="left", padx=2)
        self.tlacitko_start = ttk.Button(ovladani, text="▶ Spustit", width=11, command=self.prepni)
        self.tlacitko_start.pack(side="left", padx=2)
        ttk.Button(ovladani, text="Vpřed ▶", width=9, command=lambda: self.o_krok(1)).pack(side="left", padx=2)
        ttk.Button(ovladani, text="⏭", width=4, command=lambda: self.jdi_na(len(self.snimky) - 1)).pack(side="left")

        ttk.Label(ovladani, text="Rychlost:").pack(side="left", padx=(20, 5))
        self.rychlost = ttk.Scale(ovladani, from_=0, to=100, length=150)
        self.rychlost.set(45)
        self.rychlost.pack(side="left")

        ttk.Label(ovladani, text="Průběh:").pack(side="left", padx=(20, 5))
        self.posuvnik = ttk.Scale(ovladani, from_=0, to=1, command=self._posuvnik_zmena)
        self.posuvnik.pack(side="left", fill="x", expand=True)

        # legenda
        self.legenda = ttk.Frame(hlavni)
        self.legenda.pack(fill="x", pady=(8, 0))

        # vysvětlení algoritmu
        ramec = ttk.LabelFrame(hlavni, text=" Jak to funguje ", padding=8)
        ramec.pack(fill="x", pady=(10, 0))
        self.text = tk.Text(ramec, height=5, wrap="word", font=("Segoe UI", 10), relief="flat",
                            background=self.cget("background"), borderwidth=0)
        self.text.tag_configure("tucne", font=("Segoe UI", 10, "bold"))
        self.text.pack(fill="x")

        ttk.Label(hlavni, text="Ovládání z klávesnice: mezerník = spustit/pozastavit, šipky = krok, Home/End = začátek/konec",
                  foreground="#78909c").pack(anchor="w", pady=(6, 0))

    # ---------------------------------------------------------------- data a nahrávání
    def _nova_data(self):
        try:
            n = int(self.pocet.get())
        except (tk.TclError, ValueError):
            n = 14
        n = max(MIN_PRVKU, min(MAX_PRVKU, n))
        self.pocet.set(n)
        self.data = random.sample(range(1, n + 1), n)
        self._preved()

    def _pouzij_vlastni(self):
        casti = [c for c in re.split(r"[,;\s]+", self.vlastni.get().strip()) if c]
        try:
            cisla = [int(c) for c in casti]
        except ValueError:
            cisla = None
        if cisla is None or not (MIN_PRVKU <= len(cisla) <= MAX_PRVKU):
            messagebox.showerror("Špatný vstup",
                                 f"Zadej {MIN_PRVKU} až {MAX_PRVKU} celých čísel oddělených čárkou, třeba: 5, 2, 9, 1, 7")
            return
        self.data = cisla
        self.pocet.set(len(cisla))
        self._preved()

    def _nacti_ze_souboru(self):
        cesta = filedialog.askopenfilename(title="Vyber soubor s čísly",
                                           filetypes=[("Textové soubory", "*.txt")])
        if not cesta:
            return  # uživatel dialog zavřel
        try:
            cisla = nacti_soubor(cesta)
        except (OSError, ValueError) as chyba:  # UnicodeDecodeError je taky ValueError
            messagebox.showerror("Soubor nejde načíst", f"{cesta}\n\n{chyba}")
            return
        # čísla dám do pole "Vlastní čísla", kontrolu počtu už udělá _pouzij_vlastni
        self.vlastni.delete(0, "end")
        self.vlastni.insert(0, ", ".join(map(str, cisla)))
        self._pouzij_vlastni()

    def _zmena_algoritmu(self):
        self._preved()

    def _preved(self):
        """Spustí vybraný algoritmus na aktuálních datech a zapíše si všechny kroky."""
        self.pozastav()
        nazev = self.vyber.get()
        self.snimky = nahraj_snimky(ALGORITMY[nazev], self.data)
        self.cas = zmer_cas(ALGORITMY[nazev], self.data)   # zvlášť, bez zapisování kroků
        self.poloha = 0
        self._nastavuji = True
        self.posuvnik.configure(to=max(1, len(self.snimky) - 1))
        self._nastavuji = False
        self._obnov_legendu(nazev)
        self._obnov_popis(nazev)
        self._ukaz()

    def _obnov_legendu(self, nazev):
        for w in self.legenda.winfo_children():
            w.destroy()
        for klic, popisek in LEGENDA[nazev]:
            ctverec = tk.Frame(self.legenda, width=14, height=14, bg=BARVY[klic])
            ctverec.pack(side="left")
            ttk.Label(self.legenda, text=popisek).pack(side="left", padx=(4, 14))

    def _obnov_popis(self, nazev):
        princip, slozitost = POPISY[nazev]
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", nazev + ": ", "tucne")
        self.text.insert("end", princip + "\n")
        self.text.insert("end", "Složitost: ", "tucne")
        self.text.insert("end", slozitost)
        self.text.configure(state="disabled")

    # ---------------------------------------------------------------- vykreslení
    def _ukaz(self):
        s = self.snimky[self.poloha]
        self.popis_kroku.configure(text=s.text)
        posledni = len(self.snimky) - 1
        self.pocitadla.configure(
            text=f"Krok {self.poloha} z {posledni}     Porovnání: {s.porovnani}     "
                 f"Prohození / přesuny: {s.prohozeni}     "
                 f"Čas řazení (bez animace): {format_casu(self.cas)}")
        self._nastavuji = True
        self.posuvnik.set(self.poloha)
        self._nastavuji = False
        self._vykresli()

    def _vykresli(self):
        if not self.snimky:
            return
        c = self.platno
        c.delete("all")
        w = max(c.winfo_width(), 100)
        h = max(c.winfo_height(), 100)
        s = self.snimky[self.poloha]
        n = len(s.stav)

        okraj = 16
        dno = h - 24                    # kde sloupce začínají (pod nimi jsou indexy)
        vrch = 32                       # nahoře nechám místo na čísla
        mn, mx = min(s.stav), max(s.stav)
        sirka = (w - 2 * okraj) / n
        mezera = 2 if sirka < 12 else 4

        for i, hodnota in enumerate(s.stav):
            vyska = (hodnota - mn + 1) / (mx - mn + 1) * (dno - vrch)
            x0 = okraj + i * sirka + mezera / 2
            x1 = okraj + (i + 1) * sirka - mezera / 2
            role = s.barvy.get(i)
            if role is None:
                role = "hotovo" if i in s.hotovo else "obycejny"
            c.create_rectangle(x0, dno - vyska, x1, dno, fill=BARVY[role], outline="")
            stred = (x0 + x1) / 2
            if n <= 30:
                c.create_text(stred, dno - vyska - 10, text=str(hodnota), font=("Segoe UI", 10, "bold"),
                              fill="#263238")
            if n <= 40:
                c.create_text(stred, dno + 11, text=str(i), font=("Segoe UI", 8), fill="#90a4ae")

    # ---------------------------------------------------------------- přehrávání
    def prepni(self):
        if self.bezi:
            self.pozastav()
        else:
            if self.poloha >= len(self.snimky) - 1:   # na konci se začíná znovu
                self.poloha = 0
            self.bezi = True
            self.tlacitko_start.configure(text="⏸ Pauza")
            self._tik()

    def pozastav(self):
        self.bezi = False
        if self.uloha is not None:
            self.after_cancel(self.uloha)
            self.uloha = None
        self.tlacitko_start.configure(text="▶ Spustit")

    def _zpozdeni(self):
        # od 1000 ms (úplně vlevo) po 4 ms (úplně vpravo), plynule
        return max(1, int(1000 * (0.004 ** (float(self.rychlost.get()) / 100))))

    def _tik(self):
        if not self.bezi:
            return
        if self.poloha < len(self.snimky) - 1:
            self.poloha += 1
            self._ukaz()
            self.uloha = self.after(self._zpozdeni(), self._tik)
        else:
            self.pozastav()

    def o_krok(self, smer):
        self.pozastav()
        self.jdi_na(self.poloha + smer)

    def jdi_na(self, kam):
        self.pozastav()
        self.poloha = max(0, min(len(self.snimky) - 1, kam))
        self._ukaz()

    def _posuvnik_zmena(self, hodnota):
        if self._nastavuji:
            return
        self.pozastav()
        self.poloha = max(0, min(len(self.snimky) - 1, int(float(hodnota))))
        self._ukaz()

    def _klavesa(self, akce):
        # když píšu do políčka, mezerník a šipky nemají ovládat přehrávání
        if isinstance(self.focus_get(), (tk.Entry, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            return
        akce()

    def _zavri(self):
        self.pozastav()
        self.destroy()


# ---------------------------------------------------------------------------
# Zkouška, že všechno funguje
# ---------------------------------------------------------------------------
def _otestuj():
    algoritmy = list(ALGORITMY.items())

    # stejná čísla, jaká používám v protokolu
    priklad = [7, 3, 9, 5, 1, 8, 2, 6]
    print("Vstup:", priklad)
    for nazev, funkce in algoritmy:
        print(f"  {nazev:<15} -> {funkce(priklad)}   čas řazení {format_casu(zmer_cas(funkce, priklad))}")

    # krajní případy: prázdný seznam, jeden prvek, seřazený, obrácený,
    # samé stejné hodnoty, záporná čísla a duplicity
    zvlastni = [
        [],
        [4],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [2, 2, 2, 2],
        [3, -1, 0, -7, 3, 12, -1],
    ]

    # plus pár stovek náhodných seznamů, výsledek porovnám se sorted()
    nahodne = [[random.randint(-50, 50) for _ in range(random.randint(0, 40))]
               for _ in range(300)]

    vse_ok = True
    for nazev, funkce in algoritmy:
        for seznam in zvlastni + nahodne:
            kopie = list(seznam)
            if funkce(seznam) != sorted(seznam) or seznam != kopie:
                print(f"CHYBA: {nazev} špatně seřadil {seznam}")
                vse_ok = False

            # záznam kroků pro okno nesmí řazení nijak ovlivnit
            snimky = nahraj_snimky(funkce, seznam)
            if snimky[-1].stav != sorted(seznam) or any(sorted(s.stav) != sorted(seznam) for s in snimky):
                print(f"CHYBA: záznam kroků u {nazev} nesedí pro {seznam}")
                vse_ok = False
    # načítání ze souboru (None = má vyhodit ValueError)
    pripady = [
        ("5 3 -2\n10,7;0\n\n", [5, 3, -2, 10, 7, 0]),
        ("﻿1\n2\n3", [1, 2, 3]),  # BOM z Poznámkového bloku
        ("", []),
        ("1 2 abc", None),
        ("1.5 2", None),
    ]
    for obsah, ocekavam in pripady:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(obsah)
        try:
            vysledek = nacti_soubor(f.name)
        except ValueError:
            vysledek = None
        finally:
            os.remove(f.name)
        if vysledek != ocekavam:
            print(f"CHYBA: nacti_soubor({obsah!r}) vrátil {vysledek}, čekal jsem {ocekavam}")
            vse_ok = False

    print("\nVšechny testy prošly." if vse_ok else "\nNěkde je chyba!")


if __name__ == "__main__":
    # aby se česká písmena správně vypsala i v konzoli na Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if "--test" in sys.argv:
        _otestuj()
    else:
        Okno().mainloop()
