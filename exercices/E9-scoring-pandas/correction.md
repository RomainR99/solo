# E9 — Correction : rejouer le scoring

Jeu utilisé : `data/sessions.csv` (le dataset d'exemple du dossier, 12 sessions). Le CSV d'E8 n'a pas la colonne `label` ni les signaux séparés par `|`.

```bash
python starter.py
```

## 1. Recalcul

`botScore` est le maximum des niveaux, chaque niveau étant la somme de ses poids plafonnée à 1. Un signal dur (`webdriver`, `headless_ua`, `selenium`, …) force 1 et le verdict `bot`. Sinon `net = botScore − min(trust, 0,15)`, puis `net ≥ 0,8` → `bot`, `≥ 0,4` → `suspect`, sinon `clean`.

**Accord des verdicts avec SOLO : 100 %** (12/12).

| Client | SOLO | Recalculé | net |
|---|---|---|---|
| chrome-humain-1 | clean | clean | 0,0 |
| chrome-humain-2 | clean | clean | 0,0 |
| firefox-humain | clean | clean | 0,0 |
| safari-humain | clean | clean | 0,1 |
| chrome-vpn-humain | suspect | suspect | 0,7 |
| chrome-sans-interaction | clean | clean | 0,2 |
| curl | suspect | suspect | 0,7 |
| python-requests | bot | bot | 1,0 |
| playwright-headless | bot | bot | 1,0 |
| selenium-dc | bot | bot | 1,0 |
| bot-essaim | bot | bot | 1,0 |
| bot-env-vm | bot | bot | 1,0 |

Le net n'est pas toujours égal à la colonne `bot_score`. SOLO y met parfois le score brut du niveau : le VPN humain est à 0,8 dans le CSV (0,4 + 0,4) et le net vaut 0,7 après le crédit de 0,10. `python-requests` (0,7 + 0,4) et `bot-env-vm` (0,65 + 0,65) sont plafonnés à 1 ici, le CSV les note 0,9 et 0,85. Le verdict, lui, ne bouge pas.

## 2. Matrice de confusion

Positif = verdict `bot` ou `suspect`. Négatif = `clean`. La vérité est la colonne `label`.

```text
[[5 1]
 [0 6]]
```

|  | Prédit humain | Prédit bot/suspect |
|---|---|---|
| Vrai humain (6) | 5 | 1 |
| Vrai bot (6) | 0 | 6 |

Le seul écart est `chrome-vpn-humain` : un humain, retenu en `suspect` (net 0,7). Précision bot/suspect 0,86, rappel 1,00, accuracy 0,92.

## 3. Seuil `review` de 0,2 à 0,8

`block` reste à 0,8. On ne fait varier que le seuil à partir duquel une session est retenue.

| review | Précision | Rappel |
|---|---|---|
| 0,2 | 0,75 | 1,00 |
| 0,3 à 0,7 | 0,86 | 1,00 |
| 0,8 | 1,00 | 0,83 |

À 0,2, le Chrome sans interaction (net 0,2, humain) est retenu en plus : la précision tombe. De 0,3 à 0,7, le seul humain retenu est le VPN (0,7) et tous les bots le sont, y compris curl (0,7). À 0,8, plus personne à 0,7 n'est retenu : la précision passe à 1, curl échappe, le rappel tombe à 0,83.

**E-commerce : `review = 0,8`.** Un faux positif bloque un achat. Le client au VPN (0,7) doit passer. On accepte de laisser passer un client du niveau de curl. On ne durcit que ce qui atteint le seuil `bot`.

**Formulaire de vote : `review = 0,3`.** Un faux négatif compte une voix de bot. 0,3 est le bas du plateau où le rappel vaut encore 1, sans reprendre le visiteur immobile à 0,2. Le VPN humain part en revue : on lui redemande une confirmation, on ne jette pas son bulletin automatiquement.

## Bonus — arbre

Un arbre de profondeur 3 ne retient que trois questions : `tls_ua_mismatch`, `webdriver`, `rep_fp_many_ips`. Il classe `selenium-dc` et `bot-env-vm` comme humains. Il ne retrouve pas les poids de SOLO : le moteur additionne des signaux mous par niveau, l'arbre cherche une coupure unique sur 12 lignes.
