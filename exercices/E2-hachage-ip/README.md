# E2 — Hacher une IP ne l'anonymise pas (25 min, Python)

**Objectif.** Montrer qu'un hash d'une donnée à faible entropie se casse par force brute,
et qu'un HMAC avec clé secrète corrige le problème tout en gardant les agrégats.

## Fichiers

- `data/hashes.txt` : 20 empreintes `sha256(ip)` d'un faux export SOLO.
  Les IP sont toutes dans `203.0.113.0/24` (bloc de documentation, RFC 5737).
- `starter.py` : squelette à compléter.
- Sel public pour la partie 3 : `solo-labo-b3-2026`.

## Étapes

1. **Brute-force le /24.** Les 20 IP sont dans `203.0.113.0/24` (256 possibilités).
   Retrouve-les toutes. Combien de temps ça prend ?
2. **Extrapole.** Combien de hash faudrait-il tester pour couvrir **tout** IPv4 (2³² ≈ 4,3
   milliards) ? Estime le temps sur ta machine, puis sur un GPU (≈ 10 milliards de SHA-256/s).
3. **HMAC.** Recommence avec `hmac.new(cle, ip, sha256)` et une clé que tu ne donnes pas à
   « l'attaquant ». Montre que le brute-force ne retrouve plus rien sans la clé.
4. **Discussion.** HMAC = pseudonymisation : la donnée reste **personnelle** au sens du RGPD,
   mais on garde la possibilité de faire `GROUP BY` / `COUNT DISTINCT` (même entrée → même sortie).

## Livrable

Un notebook (ou script) avec le temps mesuré au /24, l'extrapolation à IPv4, et une réponse
écrite à : **« pourquoi SOLO ne peut-il pas simplement stocker `sha256(ip)` ? »**
