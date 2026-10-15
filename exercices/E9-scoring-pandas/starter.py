#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E9 — rejouer le scoring de SOLO en pandas. Complète les TODO.
Nécessite : pip install pandas scikit-learn"""
import os
import pandas as pd
from config_extract import WEIGHTS, HARD_SIGNALS, LEVEL_OF, BLOCK, REVIEW, MAX_FORGEABLE_OFFSET

HERE = os.path.dirname(os.path.abspath(__file__))


def score_ligne(signaux: list[str], confiance_forgeable: float) -> tuple[float, str, bool]:
    """Reproduit max(niveaux) - confiance, puis applique les seuils."""
    if any(s in HARD_SIGNALS for s in signaux):
        return 1.0, "bot", True                      # signal dur -> bot forcé
    par_niveau = {}
    for s in signaux:
        lvl = LEVEL_OF.get(s)
        if lvl is None:
            continue
        par_niveau[lvl] = par_niveau.get(lvl, 0.0) + WEIGHTS[lvl][s]
    bot_score = min(1.0, max(par_niveau.values(), default=0.0))   # max ENTRE niveaux
    offset = min(confiance_forgeable, MAX_FORGEABLE_OFFSET)
    net = max(0.0, bot_score - offset)
    verdict = "bot" if net >= BLOCK else "suspect" if net >= REVIEW else "clean"
    return round(net, 3), verdict, False


def main():
    df = pd.read_csv(os.path.join(HERE, "data", "sessions.csv"))
    df["signaux_list"] = df["signaux"].fillna("").apply(
        lambda x: [s for s in x.split("|") if s])

    # 1) recalcul
    res = df.apply(lambda r: score_ligne(r["signaux_list"], r.get("trust_score", 0.0)), axis=1)
    df["net_calcule"] = [r[0] for r in res]
    df["verdict_calcule"] = [r[1] for r in res]
    accord = (df["verdict_calcule"] == df["verdict_solo"]).mean()
    print(f"[1] accord verdict recalculé vs SOLO : {accord*100:.0f} %")
    print(df[["client", "verdict_solo", "verdict_calcule", "net_calcule"]].to_string(index=False))

    # 2) matrice de confusion (humain vs bot)
    try:
        from sklearn.metrics import confusion_matrix, classification_report
        y_true = (df["label"] == "bot").astype(int)
        y_pred = df["verdict_calcule"].isin(["bot", "suspect"]).astype(int)  # suspect = traité comme non-humain
        print("\\n[2] matrice de confusion [humain, bot] :")
        print(confusion_matrix(y_true, y_pred))
        print(classification_report(y_true, y_pred, target_names=["humain", "bot/suspect"], zero_division=0))
    except ImportError:
        print("[2] installe scikit-learn pour la matrice de confusion")

    # 3) TODO : balayer REVIEW de 0.2 à 0.8, tracer précision/rappel, choisir le seuil
    #    pour un e-commerce (tolère les faux négatifs) vs un vote (tolère les faux positifs).


if __name__ == "__main__":
    main()
