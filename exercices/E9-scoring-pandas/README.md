# E9 — Rejouer le scoring en pandas (25 min, Python)

**Objectif.** Recalculer le `botScore` de SOLO à la main, mesurer les erreurs, et comprendre
que le seuil est un choix métier.

## Fichiers

- `data/sessions.csv` : dataset d'exemple (une ligne par session, signaux déclenchés + verdict
  de référence). En vrai cours, utilise **le CSV de la promo produit en E8**.
- `config_extract.py` : les poids et seuils **extraits de `src/shared/decision/config.ts`**
  (version `n1n2n3n4n5-trust-2026.06.8`).
- `starter.py` : squelette.

## Rappel du moteur (cf. C9)

- Chaque niveau **additionne** les poids de ses signaux, **plafonné à 1**.
- `botScore` = le **maximum** des niveaux (pas la somme).
- `net = botScore − confiance` (part forgeable de la confiance plafonnée à 0,15).
- Seuils : `net ≥ 0,8` → `bot` ; `≥ 0,4` → `suspect` ; sinon `clean`.

## Étapes

1. **Recalculer.** À partir des signaux de chaque ligne et des poids de `config_extract.py`,
   calcule `botScore` (somme par niveau, puis max) et compare à la colonne `bot_score` de SOLO.
2. **Matrice de confusion.** Étiquette chaque session (humain / bot) d'après le client, puis
   `sklearn.metrics.confusion_matrix` et `classification_report`.
3. **Balayer le seuil.** Fais varier le seuil `review` de 0,2 à 0,8 et trace précision / rappel.
   Où le mettrais-tu pour un **site e-commerce** ? pour un **formulaire de vote** ?
4. **Bonus.** Entraîne un `DecisionTreeClassifier` sur les signaux et compare ses règles à SOLO.

## Livrable

Le notebook, la matrice de confusion, et le seuil choisi (justifié) pour e-commerce puis pour vote.
