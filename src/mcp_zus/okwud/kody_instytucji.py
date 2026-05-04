"""Słownik kodów instytucji uprawnionych do złożenia wniosku OK-WUD.

Source: ZUS — "Wytyczne techniczne dla komunikacji bezpośredniej z ZUS"
(BIP ZUS / Wymagania dla oprogramowania interfejsowego).
"""
from __future__ import annotations

KODY_INSTYTUCJI: dict[str, str] = {
    "ABW": "Agencja Bezpieczeństwa Wewnętrznego",
    "AMW": "Agencja Mienia Wojskowego",
    "AW": "Agencja Wywiadu",
    "BANK": "NBP i inne banki",
    "BE": "Biura Emerytalne",
    "BNW": "Biuro Nadzoru Wewnętrznego",
    "CBA": "Centralne Biuro Antykorupcyjne",
    "CPR": "Centrum Pomocy Rodzinie",
    "GIIF": "Generalny Inspektor Informacji Finansowej",
    "IPN": "Instytut Pamięci Narodowej",
    "KAS": "Krajowa Administracja Skarbowa",
    "KNF": "Komisja Nadzoru Finansowego",
    "KRUS": "KRUS",
    "KS": "Komornik Sądowy",
    "KUR": "Kurator sądowy",
    "MF": "Minister właściwy ds. finansów",
    "MG": "Minister właściwy ds. gospodarki",
    "MP": "Minister właściwy ds. Pracy",
    "MR": "Minister właściwy ds. rodziny",
    "MRR": "Minister właściwy do spraw rozwoju regionalnego",
    "MW": "Marszałek Województwa",
    "MZS": "Minister właściwy ds. zabezpieczenia społecznego",
    "NFZ": "Narodowy Fundusz Zdrowia",
    "NIK": "Najwyższa Izba Kontroli",
    "OEG": "Organy egzekucyjne inne niż komornicy sądowi",
    "OFE": "OFE",
    "OKS": "Organy Kontroli Skarbowej",
    "OP": "Organy Podatkowe",
    "OPS": "Ośrodki Pomocy Społecznej",
    "ORS": "Ośrodki realizujące świadczenia rodzinne, alimentacyjne, wychowawcze",
    "P": "Prokuratorzy",
    "PCPR": "Powiatowe Centra Pomocy Rodzinie",
    "PFRON": "Państwowy Fundusz Rehabilitacji Osób Niepełnosprawnych",
    "PIP": "Państwowa Inspekcja Pracy",
    "PIS": "Państwowa Inspekcja Sanitarna",
    "POLICJA": "Policja",
    "PS": "Posłowie i Senatorowie",
    "PSZ": "Publiczne służby zatrudnienia",
    "PTA": "Prokuratoria",
    "PUP": "Powiatowe Urzędy Pracy",
    "PZ": "Podmioty zagraniczne",
    "REP": "Komisja ds. reprywatyzacji nieruchomości warszawskich",
    "RPD": "Rzecznik Praw Dziecka",
    "RPO": "Rzecznik Praw Obywatelskich",
    "S": "Sądy",
    "SG": "Straż Graniczna",
    "SKCIK": "Szef Krajowego Centrum Informacji Kryminalnych",
    "SKO": "Samorządowe Kolegium Odwoławcze",
    "SKW": "Służba Kontrwywiadu Wojskowego",
    "ST": "Starosta",
    "SUSCW": "Szef Urzędu do Spraw Cudzoziemców, Wojewoda",
    "UC": "Urząd Celny/Izba Celna",
    "USKAS": "Urząd Skarbowy - organ KAS",
    "USOE": "Urząd Skarbowy - organ egzekucyjny",
    "USOP": "Urząd Skarbowy - organ podatkowy",
    "USW": "Urząd Skarbowy - wierzyciel",
    "UTK": "Urząd Transportu Kolejowego",
    "W": "Wojewoda",
    "WBE": "Wojskowe Biuro Emerytalne",
    "WBPM": "Wójt, Burmistrz oraz Prezydent Miasta",
    "WCU": "Wojewoda - ws. cudzoziemców",
    "WUP": "Wojewódzki Urząd Pracy",
    "ZM": "Związek Międzygminny",
    "ZW": "Żandarmeria Wojskowa",
}


def is_valid_kod(kod: str) -> bool:
    return kod in KODY_INSTYTUCJI


def describe_kod(kod: str) -> str | None:
    return KODY_INSTYTUCJI.get(kod)


__all__ = ["KODY_INSTYTUCJI", "describe_kod", "is_valid_kod"]
