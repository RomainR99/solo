# E3 — Atelier JWT (25 min, Python)

**Objectif.** Décoder un JWT, repérer ce qui ne doit pas y figurer, comprendre `alg:none`
et casser un secret faible.

## Fichiers

- `data/tokens.txt` : trois JWT (`token1`, `token2`, `token3`).
- `data/wordlist.txt` : petite liste de secrets candidats.
- `starter.py` : squelette.

## Étapes

1. **Décoder.** Décode les trois tokens **sans vérifier la signature** (header + payload sont
   du Base64URL). Fais-le d'abord à la main (ou avec `base64`), puis avec PyJWT.
   → **Lequel contient une donnée qui ne devrait jamais être dans un JWT ?** Pourquoi ?
2. **`alg:none`.** Forge un token avec `"alg":"none"` et sans signature. Montre qu'un vérifieur
   naïf l'accepte, puis corrige en imposant `algorithms=["HS256"]`.
3. **Secret faible.** Un des tokens est signé en HS256 avec un secret présent dans `wordlist.txt`.
   Retrouve-le par essai de chaque mot. Lequel est-ce ?
4. **Bonus.** Signe un token en ES256 (clé privée/publique) et explique pourquoi un service tiers
   peut le vérifier sans pouvoir en forger.

## Rappels

- Base64URL **n'est pas du chiffrement** : le payload est lisible par tout le monde.
- Toujours vérifier au minimum : la signature (algorithme **fixé**), `exp`, `aud`.

## Livrable

Le token `alg:none` forgé, le secret faible retrouvé, et le `jwt.decode(...)` **correct**.
