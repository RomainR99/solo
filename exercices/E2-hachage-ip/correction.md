# E2 — Correction : hacher une IP ne l'anonymise pas

Depuis `exercices/E2-hachage-ip` :

```bash
source .venv/bin/activate
python starter.py
```

Mesures obtenues avec ces commandes sur cette machine (Python 3.12, venv du dossier). Les 20 empreintes de `data/hashes.txt` sont des `sha256(ip)` dont les IP sont toutes dans `203.0.113.0/24`.

## 1. Brute-force du /24

256 adresses testées, **20/20 IP retrouvées en 0,2 ms**.

```
203.0.113.39
203.0.113.45
203.0.113.82
203.0.113.85
203.0.113.91
203.0.113.92
203.0.113.112
203.0.113.124
203.0.113.131
203.0.113.135
203.0.113.140
203.0.113.152
203.0.113.163
203.0.113.174
203.0.113.187
203.0.113.197
203.0.113.204
203.0.113.207
203.0.113.208
203.0.113.240
```

Le hash n'a pas de clé. Pour chaque IP du bloc on recalcule `sha256(ip)` et on compare au fichier. Dès que le digest correspond, l'IP d'origine est retrouvée.

## 2. Extrapolation à tout IPv4

| Mesure | Valeur |
|---|---|
| Débit sur cette machine | ~909,9 ns / hash |
| IPv4 complet (2³² ≈ 4,3 milliards) sur cette machine | ~65,1 min |
| Même espace sur un GPU (~10 milliards de SHA-256/s) | ~0,43 s |

Un /24 tombe en moins d'une milliseconde. Tout l'espace IPv4 tient en environ une heure sur ce Mac, et en moins d'une seconde sur un GPU.

## 3. HMAC

Les 20 IP retrouvées à l'étape 1 sont rehachées avec `hmac.new(cle, ip, sha256)`. Le script reteste ensuite les 256 adresses du /24.

`HMAC-SHA256` de `203.0.113.42` avec la clé secrète :

```
79b725570404190e7e184e0d…
```

| Calcul de l'attaquant | Résultat |
|---|---|
| `sha256(sel public + ip)`, sel `solo-labo-b3-2026` connu | **20/20** en 0,2 ms |
| `sha256(ip)` contre les HMAC à clé secrète | **0/20** en 0,2 ms |
| `HMAC(sel public, ip)` contre ces mêmes HMAC | **0/20** en 0,4 ms |
| `HMAC(clé secrète, ip)` | **20/20** en 0,4 ms |

## Ce qu'on en déduit

Un `sha256` d'IP, même salé avec une valeur publique, se casse. Un HMAC ne tient que tant que la clé reste secrète.

Le /24 tombe en moins d'une milliseconde, et tout l'IPv4 tient en **65 minutes** sur cette machine, **0,43 s** sur un GPU. Une adresse IP a trop peu de valeurs possibles pour qu'un hash rapide la cache.

Le sel `solo-labo-b3-2026` ne change rien : il est dans le script, donc l'attaquant le concatène et retrouve **20/20** IP. Un sel n'est utile que s'il est secret.

Sans la clé, les deux essais contre les HMAC donnent **0/20** : `sha256(ip)` comme `HMAC(sel public, ip)`. Avec la clé, le même parcours retrouve **20/20**. La protection est la clé, pas l'algorithme.

Ce HMAC reste une pseudonymisation. La même IP redonne toujours le même digest, donc un `COUNT(DISTINCT)` marche encore pour qui possède la clé, et cette personne peut aussi refaire le brute-force. La donnée reste personnelle au sens du RGPD.

## Pourquoi SOLO ne peut-il pas simplement stocker `sha256(ip)` ?

Parce qu'une IP n'a presque pas d'entropie. Il n'existe que 2³² valeurs IPv4, et souvent beaucoup moins (un /24, le parc d'un FAI). SHA-256 est rapide et déterministe : qui possède le hash peut retester les IP candidates et retrouver l'originale, comme ci-dessus en 0,2 ms. Un sel public ne change rien : les 20 IP retombent aussi en 0,2 ms. Le hash sans clé secrète ne fait donc pas d'anonymisation.

Un HMAC avec une clé que l'attaquant n'a pas empêche ce recalcul. Ce n'est toujours pas de l'anonymisation : c'est une **pseudonymisation**. La donnée reste personnelle au sens du RGPD, puisque le détenteur de la clé peut revenir à l'IP, et la stabilité du HMAC permet encore de compter les visites distinctes.
