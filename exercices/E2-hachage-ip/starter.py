#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2 — hacher une IP ne l'anonymise pas. À compléter aux endroits TODO."""
import hashlib, hmac, ipaddress, time, os

HERE = os.path.dirname(os.path.abspath(__file__))
SEL_PUBLIC = b"solo-labo-b3-2026"      # connu de tous
CLE_SECRETE = b"la-cle-que-l-attaquant-n-a-pas"   # pour la partie 3


def charger_hashes():
    cibles = set()
    with open(os.path.join(HERE, "data", "hashes.txt")) as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#"):
                cibles.add(ligne)
    return cibles


def partie1_bruteforce_24(cibles):
    """TODO : parcourir 203.0.113.0/24, hacher chaque IP, retrouver les 20."""
    t0 = time.time()
    trouvees = {}
    for ip in ipaddress.ip_network("203.0.113.0/24"):
        h = hashlib.sha256(str(ip).encode()).hexdigest()   # <-- le geste à comprendre
        if h in cibles:
            trouvees[str(ip)] = h
    dt = time.time() - t0
    print(f"[P1] {len(trouvees)}/20 IP retrouvées en {dt*1000:.1f} ms")
    for ip in sorted(trouvees, key=lambda x: int(x.split('.')[-1])):
        print("   ", ip)
    return dt


def partie2_extrapolation(dt_24):
    # TODO : à partir du temps pour 256 hash, estimer le temps pour 2**32.
    par_hash = dt_24 / 256
    total_ipv4 = 2 ** 32
    print(f"[P2] ~{par_hash*1e9:.1f} ns / hash sur cette machine")
    print(f"[P2] IPv4 complet sur cette machine : ~{par_hash*total_ipv4/60:.1f} min")
    print(f"[P2] sur un GPU (~1e10 h/s) : ~{total_ipv4/1e10:.2f} s")


def _compter(reseau, cibles, etiquette):
    """Reteste chaque IP du /24. `etiquette(ip) -> digest` est le calcul de l'attaquant."""
    t0 = time.time()
    trouvees = []
    for ip in reseau:
        if etiquette(str(ip).encode()) in cibles:
            trouvees.append(str(ip))
    return trouvees, time.time() - t0


def partie3_hmac(ips):
    """Les cibles sont des HMAC à clé secrète. Sans cette clé, le /24 ne donne rien."""
    reseau = ipaddress.ip_network("203.0.113.0/24")
    cibles_hmac = {
        hmac.new(CLE_SECRETE, ip.encode(), hashlib.sha256).hexdigest() for ip in ips
    }
    exemple = "203.0.113.42"
    pseudo = hmac.new(CLE_SECRETE, exemple.encode(), hashlib.sha256).hexdigest()
    print(f"[P3] HMAC({exemple}) = {pseudo[:24]}…")

    # Sel public : connu de l'attaquant, donc il le concatène et le /24 retombe.
    cibles_sel = {
        hashlib.sha256(SEL_PUBLIC + ip.encode()).hexdigest() for ip in ips
    }
    avec_sel, dt_sel = _compter(
        reseau, cibles_sel, lambda raw: hashlib.sha256(SEL_PUBLIC + raw).hexdigest()
    )
    print(f"[P3] sha256(sel public + ip) : {len(avec_sel)}/20 en {dt_sel*1000:.1f} ms")

    # HMAC : l'attaquant n'a pas CLE_SECRETE. sha256 nu et HMAC au sel public ratent.
    sans_cle, dt_nu = _compter(
        reseau, cibles_hmac, lambda raw: hashlib.sha256(raw).hexdigest()
    )
    mauvais_sel, dt_mauvais = _compter(
        reseau, cibles_hmac, lambda raw: hmac.new(SEL_PUBLIC, raw, hashlib.sha256).hexdigest()
    )
    avec_cle, dt_cle = _compter(
        reseau, cibles_hmac, lambda raw: hmac.new(CLE_SECRETE, raw, hashlib.sha256).hexdigest()
    )
    print(f"[P3] sans la clé, sha256(ip) contre les HMAC : {len(sans_cle)}/20 en {dt_nu*1000:.1f} ms")
    print(f"[P3] sans la clé, HMAC(sel public) : {len(mauvais_sel)}/20 en {dt_mauvais*1000:.1f} ms")
    print(f"[P3] avec la clé, HMAC(clé secrète) : {len(avec_cle)}/20 en {dt_cle*1000:.1f} ms")
    print("[P3] même IP -> même HMAC => COUNT(DISTINCT) marche encore pour qui a la clé.")


if __name__ == "__main__":
    cibles = charger_hashes()
    dt = partie1_bruteforce_24(cibles)
    partie2_extrapolation(dt)
    ips = [
        str(ip)
        for ip in ipaddress.ip_network("203.0.113.0/24")
        if hashlib.sha256(str(ip).encode()).hexdigest() in cibles
    ]
    partie3_hmac(ips)
