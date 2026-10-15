# E3 — Correction : atelier JWT

Depuis `exercices/E3-jwt` :

```bash
deactivate
source .venv/bin/activate
python starter.py
```

## 1. Décodage sans vérifier la signature

```
[token1] {'sub': 'u-1042', 'aud': 'solo-export', 'scope': 'export:read', 'iat': 1792000000, 'exp': 1792000900}
[token2] {'sub': 'u-2087', 'aud': 'solo-export', 'email': 'jeanne.martin@exemple.fr', 'numero_secu': '2 85 07 75 116 042 51', 'iat': 1792000000, 'exp': 1792000900}
[token3] {'sub': 'admin', 'aud': 'solo-export', 'scope': 'export:bulk', 'iat': 1792000000, 'exp': 1792000900}
```

C'est **token2** qui contient une donnée qui ne devrait jamais être dans un JWT : l'e-mail `jeanne.martin@exemple.fr` et le numéro de sécurité sociale `2 85 07 75 116 042 51`. Le payload n'est pas chiffré, seulement encodé en Base64URL. Toute personne qui voit le token lit ces données, et un JWT circule dans les en-têtes, les journaux et le navigateur.

## 2. Token `alg:none` forgé

```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInNjb3BlIjoiZXhwb3J0OmJ1bGsifQ.
```

Un décodage sans vérification de signature l'accepte :

```
{'sub': 'admin', 'scope': 'export:bulk'}
```

La signature est vide. Le header annonce `"alg":"none"`. Le payload se donne le rôle `admin` et le scope `export:bulk`.

## 3. Secret faible

```
[P3] token3 : secret trouvé = 'soleil123'
```

`token3` est signé en HS256 avec le secret `soleil123`, présent dans `data/wordlist.txt`.
