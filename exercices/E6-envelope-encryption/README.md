# E6 — Envelope encryption & audit des secrets (25 min, Python)

**Objectif.** Mettre en œuvre une hiérarchie KEK/DEK, une rotation, le crypto-shredding,
et auditer les secrets de SOLO.

## Fichiers

- `starter.py` : squelette (une KEK, une DEK par heure, rotation, shredding).
- Pour l'audit : le dépôt SOLO (`.env.example`, `docker-compose.yml`, `.gitignore`).

## Étapes

1. **Envelope encryption.** Génère une KEK (ici simulée par une clé en mémoire, en vrai dans un
   KMS/Vault). Pour chaque heure de collecte, génère une **DEK** ; chiffre les IP de cette heure
   avec sa DEK ; stocke la DEK **chiffrée par la KEK** (jamais en clair).
2. **Rotation.** Change la KEK et re-chiffre **uniquement les DEK** (rapide). Compare au temps
   qu'aurait pris le re-chiffrement de toutes les données.
3. **Crypto-shredding.** Détruis la DEK de l'heure H. Montre que les lignes de cette heure
   deviennent **illisibles** — y compris dans une éventuelle sauvegarde.
4. **Audit de SOLO (≈ 10 min).** Dans le dépôt :
   - `git log -p | grep -i -E "key|secret|password"` : un secret a-t-il déjà été committé ?
   - `.gitignore` : `.env` et `certs/*.pem` sont-ils ignorés ?
   - `.env.example` / `docker-compose.yml` : quels secrets, où vivent-ils ?
   - Où placerais-tu la **KEK** en production ?

## Livrable

Le script (envelope + rotation + shredding), le temps **rotation DEK vs re-chiffrement complet**,
et une phrase sur où vivrait la KEK en prod.
