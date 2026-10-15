# E5 — Correction : chiffrer `ip` sans casser la réputation

Depuis `exercices/E5-chiffrement-colonne`, une fois le venv activé et `cryptography` installé :

```bash
python starter.py
```

Premier lancement, sur `data/solo_fake.db` :

```text
[0] essaims détectés sur ip en clair : [('d20aa1cffb3ac01f80006c967c3535501db58a6cc0d08c29460842b084d19860', 14)]
[2] essaims sur ip_enc (aléatoire) : [('d20aa1cffb3ac01f80006c967c3535501db58a6cc0d08c29460842b084d19860', 14), ('b4ab92c6e451276c82a649098408eeff4b4461ded184f91bd2974db4b7c12a3a', 12)]   <- cassé
[3] essaims sur ip_bidx (HMAC)     : [('d20aa1cffb3ac01f80006c967c3535501db58a6cc0d08c29460842b084d19860', 14)]   <- OK
```

En clair, une empreinte canvas est vue depuis **14 IP** distinctes. C'est l'essaim que la réputation doit retrouver.

Sur `ip_enc`, le même seuil en fait apparaître un second (`…b7c12a3a`, 12). AES-256-GCM tire un nonce au hasard à chaque ligne : deux chiffrements de la même IP sont différents, donc `COUNT(DISTINCT ip_enc)` ne compte plus les IP. Il compte des chiffrés.

Sur `ip_bidx`, le HMAC est déterministe : la même IP redonne le même index. On retrouve uniquement l'essaim de 14.

Le blind index rétablit le regroupement, et il révèle encore la fréquence. Qui possède `ip_bidx` voit quelles lignes partagent la même IP et combien de valeurs distinctes se cachent derrière une empreinte, sans lire l'adresse en clair.

## Pourquoi `reputation` (lignes 15-19)

`reputation` ne calcule pas l'empreinte canvas. Elle la prend déjà dans la table et s'en sert comme identité de la machine : toutes les lignes qui ont le même `canvas_hash` sont le même navigateur, ou la même image de bot.

```python
SELECT canvas_hash, COUNT(DISTINCT colonne) n
FROM sessions
GROUP BY canvas_hash
HAVING n >= 10
```

`colonne` est le paramètre de `reputation`. C'est le nom de la colonne de la table `sessions` dont on compte les valeurs différentes, pour un même `canvas_hash`.

Le script l'appelle trois fois :

- `"ip"` : l'adresse en clair. Quatorze adresses différentes pour le même canvas.
- `"ip_enc"` : la même adresse chiffrée. Chaque ligne a un chiffré différent, donc le compte ne suit plus les adresses.
- `"ip_bidx"` : l'index HMAC. La même adresse redonne la même valeur, et on retrouve les quatorze.

`canvas_hash` ne change pas d'un appel à l'autre. Seule la colonne comptée change.

Avec `ip`, la question est : ce canvas a-t-il été vu depuis au moins 10 adresses différentes ? Le premier lancement répond oui pour `d20aa1cf…`, avec **14** IP. C'est l'essaim. Un humain réutilise peu d'adresses pour un même canvas. Le bot fait l'inverse : **une** empreinte, **beaucoup** d'IP.

Si on casse la fonction en lui donnant `ip_enc`, ce lien disparaît. AES-GCM change le nonce à chaque ligne, donc la même IP ne retombe plus sur la même valeur. `COUNT(DISTINCT ip_enc)` ne compte plus les adresses du canvas : il compte des chiffrés. L'empreinte du bot n'est plus isolée. Le résultat ajoute un faux essaim à 12.

Pour la retrouver, il faut l'inverse du chiffrement aléatoire : une valeur stable pour une même IP. C'est le HMAC de `ip_bidx`. La même adresse redonne le même index, le `GROUP BY canvas_hash` retrouve les 14, et seulement celles-là.

## Relancer `starter.py` plante

Le script plante parce que la colonne `ip_enc` existe déjà dans la base : un second `ALTER TABLE` ne peut pas la recréer.

Au premier lancement, ces deux lignes s'exécutent et SQLite les enregistre tout de suite :

```sql
ALTER TABLE sessions ADD COLUMN ip_enc BLOB;
ALTER TABLE sessions ADD COLUMN ip_bidx TEXT;
```

Au deuxième lancement, l'exécution s'arrête à la ligne 27 de `starter.py` :

```text
sqlite3.OperationalError: duplicate column name: ip_enc
```

Les colonnes sont déjà là. `ADD COLUMN` ne remplace pas une colonne existante, et le script ne teste pas `PRAGMA table_info(sessions)` avant de l'émettre.
