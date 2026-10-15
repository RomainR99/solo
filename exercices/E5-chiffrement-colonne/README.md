# E5 — Chiffrer la colonne `ip` sans casser la réputation (25 min, Python)

**Objectif.** Comprendre le conflit entre chiffrement et analyse, et le résoudre avec un
blind index.

## Fichiers

- `data/solo_fake.db` : base SQLite au **schéma réel de SOLO**, ~470 sessions factices.
  Elle contient volontairement **un essaim de bots** : une même empreinte `canvas_hash` vue
  depuis 14 IP différentes (c'est ce que la réputation N5 doit détecter).
- `starter.py` : squelette.

## La requête à préserver

SOLO détecte les essaims avec, en gros :

```sql
SELECT canvas_hash, COUNT(DISTINCT ip) AS n_ip
FROM sessions
GROUP BY canvas_hash
HAVING n_ip >= 10;
```

## Étapes

1. **Chiffrer.** Lis `sessions` avec pandas (ou `sqlite3`), chiffre `ip` en **AES-256-GCM**
   (lib `cryptography`), stocke `nonce || ciphertext` dans une nouvelle colonne `ip_enc`.
2. **Constater la casse.** La requête de réputation ne marche plus : deux chiffrés de la même IP
   sont **différents** (nonce aléatoire), donc `COUNT(DISTINCT ip_enc)` compte faux.
3. **Blind index.** Ajoute `ip_bidx = HMAC(clé_index, ip)` (déterministe) et réécris la requête
   avec `COUNT(DISTINCT ip_bidx)`. Tu dois **retrouver le même résultat** qu'au départ.
4. **Bonus.** Ouvre la base avec SQLCipher et vérifie qu'un `strings solo_fake.db` ne montre
   plus les IP.

## Livrable

La requête de réputation **avant / après**, donnant le même essaim (14 IP), et deux phrases sur
**ce que le blind index révèle encore** (la fréquence des valeurs).
