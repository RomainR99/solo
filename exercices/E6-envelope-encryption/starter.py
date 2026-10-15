#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E6 — envelope encryption, rotation, crypto-shredding. Complète les TODO.
Nécessite : pip install cryptography"""
import os, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def wrap(kek: bytes, dek: bytes) -> bytes:
    n = os.urandom(12)
    return n + AESGCM(kek).encrypt(n, dek, None)


def unwrap(kek: bytes, blob: bytes) -> bytes:
    return AESGCM(kek).decrypt(blob[:12], blob[12:], None)


def enc(dek: bytes, pt: bytes) -> bytes:
    n = os.urandom(12)
    return n + AESGCM(dek).encrypt(n, pt, None)


def main():
    kek = AESGCM.generate_key(bit_length=256)

    # 1) une DEK par heure, chiffrée par la KEK. On simule 6 heures de collecte.
    deks, dek_chiffrees, donnees = {}, {}, {}
    for h in range(9, 15):
        dek = AESGCM.generate_key(bit_length=256)
        deks[h] = dek
        dek_chiffrees[h] = wrap(kek, dek)                      # seul le chiffré est "stocké"
        donnees[h] = [enc(dek, f"203.0.113.{h}{i}".encode()) for i in range(4000)]
    print(f"[1] {len(deks)} DEK créées et chiffrées par la KEK")

    # 2) rotation de la KEK : on ne re-chiffre QUE les DEK
    t0 = time.perf_counter()
    kek2 = AESGCM.generate_key(bit_length=256)
    dek_chiffrees = {h: wrap(kek2, unwrap(kek, blob)) for h, blob in dek_chiffrees.items()}
    t_rot = time.perf_counter() - t0
    kek = kek2
    # comparaison : re-chiffrer TOUTES les données (ce qu'on évite)
    t0 = time.perf_counter()
    total = sum(len(v) for v in donnees.values())
    for h, lst in donnees.items():
        dek = unwrap(kek, dek_chiffrees[h])
        _ = [enc(dek, b"203.0.113.x") for _ in lst]
    t_full = time.perf_counter() - t0
    print(f"[2] rotation DEK : {t_rot*1000:.2f} ms  vs  re-chiffrement complet "
          f"({total} lignes) : {t_full*1000:.2f} ms")

    # 3) crypto-shredding : on détruit la DEK de 11h
    del deks[11]  # 4000 lignes/heure pour que le contraste de temps soit visible
    dek_chiffrees.pop(11, None)
    try:
        dek = unwrap(kek, dek_chiffrees[11])
        print("[3] 11h encore lisible ?!", dek[:4])
    except KeyError:
        print("[3] DEK de 11h détruite → les 4000 lignes de 11h sont illisibles, "
              "même dans un backup. (crypto-shredding)")


if __name__ == "__main__":
    main()
