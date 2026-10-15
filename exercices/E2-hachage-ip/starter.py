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


def partie3_hmac():
    """TODO : refaire avec HMAC. Sans la clé, le brute-force échoue."""
    ip = "203.0.113.42"
    pseudo = hmac.new(CLE_SECRETE, ip.encode(), hashlib.sha256).hexdigest()
    print(f"[P3] HMAC({ip}) = {pseudo[:24]}…")
    # Un attaquant qui n'a QUE le pseudonyme et le /24 ne peut pas le recalculer
    # sans CLE_SECRETE. Mais SOLO, lui, peut : même IP -> même pseudo -> GROUP BY possible.
    print("[P3] même IP -> même pseudo => COUNT(DISTINCT) marche encore ;")
    print("     sans la clé, aucune des 256 IP ne redonne ce pseudo.")


if __name__ == "__main__":
    cibles = charger_hashes()
    dt = partie1_bruteforce_24(cibles)
    partie2_extrapolation(dt)
    partie3_hmac()
