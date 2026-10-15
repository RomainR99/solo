# E6 — Correction : envelope encryption

Depuis `exercices/E6-envelope-encryption`, venv activé :

```bash
python starter.py
```

```text
[1] 6 DEK créées et chiffrées par la KEK
[2] rotation DEK : 0.03 ms  vs  re-chiffrement complet (24000 lignes): 62.43 ms
[3] DEK de 11h détruite → les 4000 lignes de 11h sont illisibles, même dans un backup. (crypto-shredding)
```

## [1] Six DEK chiffrées par la KEK

La KEK (key encryption key) est la clé maîtresse, ici une clé AES-256 tenue en mémoire. Le script simule six heures de collecte, de 9 h à 14 h. Chaque heure reçoit sa propre DEK (data encryption key), elle aussi AES-256.

Les 4 000 IP de l'heure sont chiffrées avec la DEK de cette heure. La DEK elle-même n'est pas conservée en clair : `wrap` la chiffre avec la KEK (nonce + AES-GCM). Ce qui est « stocké », c'est `dek_chiffrees`. Pour relire une heure, il faut d'abord déchiffrer sa DEK avec la KEK, puis déchiffrer les lignes avec cette DEK. C'est l'enveloppe : une petite clé protège les données, une clé maîtresse protège les petites clés.

## [2] 0,03 ms contre 62,43 ms

Changer la KEK ne touche pas aux 24 000 lignes. Le script crée `kek2`, déchiffre les 6 DEK avec l'ancienne KEK et les rechiffre avec la nouvelle. Six petits blocs, d'où **0,03 ms**. Le message affiche « rotation DEK » : ce sont bien les DEK qui sont réenveloppées, mais la clé qui tourne est la KEK.

La comparaison rechiffre les 24 000 lignes (6 heures × 4 000). Ça prend **62,43 ms**, environ deux mille fois plus. La rotation reste un travail sur les clés, pas sur les données.

## [3] La DEK de 11 h détruite

`dek_chiffrees.pop(11)` efface l'enveloppe de 11 h, et `del deks[11]` efface la copie en clair. Les 4 000 chiffrés de cette heure sont toujours là. Sans la DEK, `unwrap` ne peut plus les ouvrir : le script tombe sur `KeyError` et affiche qu'ils sont illisibles.

Une sauvegarde qui contient ces chiffrés mais plus la DEK est dans le même état. Effacer la clé équivaut à effacer les données, sans réécrire les 4 000 lignes. C'est le crypto-shredding. Les autres heures (9 h, 10 h, 12 h, 13 h, 14 h) gardent leur DEK et restent lisibles.

En production, la KEK ne vit pas dans le dépôt ni à côté des données. Elle vit dans un KMS, un HSM ou un coffre (Vault) : le service demande le déchiffrement des DEK, il ne détient pas la clé maîtresse.
