#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E5 — chiffrer la colonne ip sans casser la réputation. Complète les TODO.
Nécessite : pip install cryptography"""
import hashlib, hmac, os, sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "solo_fake.db")

DEK = AESGCM.generate_key(bit_length=256)     # clé de chiffrement des données
CLE_INDEX = b"cle-index-demo-NE-PAS-UTILISER-EN-PROD"   # clé du blind index


def reputation(con, colonne):
    """Compte les empreintes canvas vues depuis >= 10 valeurs distinctes de `colonne`."""
    q = (f"SELECT canvas_hash, COUNT(DISTINCT {colonne}) n "
         f"FROM sessions GROUP BY canvas_hash HAVING n >= 10 ORDER BY n DESC")
    return con.execute(q).fetchall()


def main():
    con = sqlite3.connect(DB)
    print("[0] essaims détectés sur ip en clair :", reputation(con, "ip"))

    # 1) chiffrement AES-GCM (aléatoire) + 3) blind index HMAC (déterministe)
    con.execute("ALTER TABLE sessions ADD COLUMN ip_enc BLOB")
    con.execute("ALTER TABLE sessions ADD COLUMN ip_bidx TEXT")
    aes = AESGCM(DEK)
    for sid, ip in con.execute("SELECT id, ip FROM sessions").fetchall():
        nonce = os.urandom(12)
        ct = nonce + aes.encrypt(nonce, ip.encode(), None)        # TODO (déjà fait)
        bidx = hmac.new(CLE_INDEX, ip.encode(), hashlib.sha256).hexdigest()  # déterministe
        con.execute("UPDATE sessions SET ip_enc=?, ip_bidx=? WHERE id=?", (ct, bidx, sid))
    con.commit()

    # 2) la casse : le chiffré aléatoire ne regroupe plus rien
    print("[2] essaims sur ip_enc (aléatoire) :", reputation(con, "ip_enc"), "  <- cassé")
    # 3) le blind index rétablit le regroupement
    print("[3] essaims sur ip_bidx (HMAC)     :", reputation(con, "ip_bidx"), "  <- OK")

    # on pourrait maintenant effacer la colonne ip en clair :
    # con.execute("UPDATE sessions SET ip = NULL")
    con.close()


if __name__ == "__main__":
    main()
