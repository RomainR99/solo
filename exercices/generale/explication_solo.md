# SOLO, expliqué par les exercices 1 à 7

SOLO est un labo d'empreinte. Un visiteur ouvre `https://localhost:8443`, accepte la collecte, et le serveur décrit la visite : pile TLS, en-têtes HTTP, IP, navigateur, matériel, rythme de souris et de clavier. Un moteur en tire un verdict (`clean`, `suspect`, `bot`). La session vit **une heure**, puis elle est effacée.

Le schéma est dans `src/server/db.ts`. Les routes sont dans `src/server/routes.ts`. La rétention et la réputation sont dans `src/server/store.ts`.

## Sommaire

- [E1 — Ce que SOLO enregistre](#e1)
- [E2 — Pourquoi l'IP n'est pas un simple hash](#e2)
- [E3 — Ce qu'un jeton ne doit pas porter](#e3)
- [E4 — Comment on lit une session aujourd'hui](#e4)
- [E5 — Comment SOLO reconnaît un essaim](#e5)
- [E6 — Où vivrait une clé maîtresse](#e6)
- [E7 — Combien de temps la visite reste](#e7)

## E1 — Ce que SOLO enregistre

<a id="e1"></a>

Une visite est une ligne de `sessions`, plus cinq blobs JSON liés par `session_id` : `server_tls`, `server_http`, `server_ip`, `client_full`, `decisions`. Les colonnes de `sessions` sont les champs sur lesquels on filtre et on groupe (`ip`, `ja3_hash`, `ja4`, `canvas_hash`, `webgl_hash`). Le détail qui ne sert pas à un `GROUP BY` reste dans le JSON. Supprimer la session supprime les blobs, parce que chaque fille est déclarée `ON DELETE CASCADE`.

Presque tout est une donnée personnelle **indirecte**. Rien ne nomme la personne : pas de nom, pas d'e-mail. L'art. 4 du RGPD vise aussi ce qui singularise quelqu'un par recoupement. L'arrêt *Breyer* range une adresse IP dynamique dans cette catégorie, parce que le FAI peut remonter à l'abonné. SOLO la garde en clair, indexée, et la recopie dans `server_ip`. Le pays, l'ASN, le drapeau Tor et le drapeau proxy en sont déduits.

`canvas_hash`, `webgl_hash` et `ja3_hash` sont des identifiants pour la même raison. Ils ne contiennent ni nom ni e-mail. Ils sont stables et indexés pour rapprocher deux visites. Le canvas et le WebGL décrivent le rendu de la machine (GPU, pilote, OS). Le JA3 condense le ClientHello TLS : seul, il désigne une pile (Chrome, Firefox, une librairie), pas une personne ; croisé avec l'IP ou le canvas, il relie des sessions. Ce ne sont pas des données de l'article 9 : elles décrivent la machine, pas un trait du corps.

Le clavier ne stocke pas ce qui a été tapé. `src/client/behavioral/keyboard.ts` lit `e.code` (la position physique : `KeyA`, `Space`) et l'instant. Il ne lit jamais `e.key`, donc pas le caractère, et pas un mot de passe. Même ce `code` ne va pas en base. L'agrégat envoyé dans `client_full` ne garde que des compteurs et des moyennes : nombre de frappes, temps d'enfoncement, temps entre deux touches, part de retours arrière. Il n'y a pas de colonne clavier dans `sessions`.

`client_full` est le JSON intégral du fingerprint navigateur. `writeClientCols` écrit deux fois le même objet : une projection dans les colonnes (`platform`, `canvas_hash`, `webgl_renderer`, …) et `JSON.stringify` dans le blob. Les colonnes serveur (`ip`, `ja3`, `verdict`) ne sont pas dans ce blob : elles ont `server_ip`, `server_tls` et `decisions`. Le blob ajoute ce que les colonnes n'ont pas : la liste des polices, les voix, l'adaptateur WebGPU, et les IP locales WebRTC (`localIps`), qui désignent la machine et le réseau du visiteur.

Le verdict, `bot_score` et `trust_score` sont des jugements du labo sur la visite. Ils sont plus sensibles à la fuite qu'un fuseau horaire, sans être des données de l'article 9.

## E2 — Pourquoi l'IP n'est pas un simple hash

<a id="e2"></a>

SOLO a besoin de l'IP pour deux choses : l'enrichir (pays, ASN, Tor, proxy) et compter les adresses distinctes d'une même empreinte. Un `sha256(ip)` semble cacher l'adresse tout en restant stable, donc compatible avec un `COUNT(DISTINCT)`.

Ça ne tient pas. Une IPv4 n'a que 2³² valeurs, et souvent beaucoup moins (un /24, le parc d'un FAI). SHA-256 est rapide et sans clé. Sur la machine du labo, les 256 adresses de `203.0.113.0/24` se retrouvent en **0,2 ms** (20/20). Tout l'espace IPv4 prend environ **65 minutes** à ~910 ns par hash, et **0,43 s** sur un GPU à 10 milliards de SHA-256 par seconde. Un sel public (`solo-labo-b3-2026`) ne change rien : il est connu, l'attaquant le concatène, et les 20 IP retombent aussi en 0,2 ms.

Un HMAC avec une clé secrète bloque ce recalcul : sans la clé, 0/20 ; avec la clé, 20/20. Ce n'est pas de l'anonymisation. C'est une **pseudonymisation**. La même IP redonne le même digest, donc le `GROUP BY` marche encore, et le détenteur de la clé peut revenir à l'adresse. Au sens du RGPD, la donnée reste personnelle. C'est pour ça que SOLO ne peut pas « simplement stocker `sha256(ip)` ».

## E3 — Ce qu'un jeton ne doit pas porter

<a id="e3"></a>

SOLO n'émet pas de JWT. L'exercice porte sur le jeton qu'il faudrait si l'export était authentifié (le scope `export:read` de l'exercice 4). Le payload d'un JWT est du Base64URL : ce n'est pas du chiffrement. Quiconque voit le jeton lit le contenu, dans un en-tête, un journal ou le navigateur.

Le token2 du jeu de données met dans ce payload un e-mail et un numéro de sécurité sociale. Ce sont des données qui n'ont rien à y faire : la seconde est une donnée de l'article 9, et les deux voyagent avec le jeton. Un jeton d'export SOLO ne devrait porter qu'un sujet, une audience (`solo-export`), un scope et une expiration.

`alg: none` montre l'autre piège. Si le vérifieur ne fixe pas l'algorithme, un header `"alg":"none"` et une signature vide suffisent à se déclarer `admin` avec `export:bulk`. La vérification impose `algorithms=["HS256"]`, plus `exp` et `aud`. Le token3 est signé avec le secret `soleil123`, présent dans la wordlist : un secret faible se retrouve par essai, le jeton aussi.

Le clavier de SOLO, déjà vu en E1, suit la même idée de minimisation : on ne garde pas le texte, seulement le rythme.

## E4 — Comment on lit une session aujourd'hui

<a id="e4"></a>

SOLO n'a pas d'authentification applicative. `.env.example` le dit : `SESSION_SECRET` et `ADMIN_TOKEN` ont été retirés, parce que rien dans le code ne les lisait. En renseigner un donnait une protection qui n'existait pas.

`POST /collect` est ouvert, avec un plafond de 15 requêtes par minute. Le serveur ignore tout identifiant envoyé par le client et pose lui-même un UUID v4 (`randomUUID()`, 122 bits aléatoires). La réponse contient `recapUrl: /recap/<uuid>`. `GET /api/fp/:id` et `GET /export/:id` vérifient seulement que l'identifiant a la forme d'un UUID v4, puis renvoient la session. Connaître l'URL suffit. L'adresse est la clé. C'est une URL-capacité, pas un mot de passe et pas une signature.

L'UUID ne se devine pas. Il fuit quand même, parce qu'il est dans l'URL :

1. l'historique du navigateur ;
2. les logs d'un proxy ou d'un reverse-proxy ;
3. l'en-tête `Referer`, si la page de récap charge une ressource tierce ;
4. une capture d'écran, un partage d'écran, ou quelqu'un qui lit la barre d'adresse.

Deux autres canaux du même type : un journal applicatif qui écrit l'URL, et un copier-coller du lien dans un mail ou un chat. Le serveur ne distingue pas le visiteur de celui qui a récupéré le lien. La session ne vit qu'une heure : passé ce délai, l'URL ne mène plus à rien.

Trois acteurs n'ont pas le même besoin, donc pas le même flux :

| Acteur | Besoin | Flux | Scope | Durée |
|---|---|---|---|---|
| Visiteur | Lire son propre récap | Authorization Code + PKCE | `fp:read:self` | accès 15 min, pas de refresh |
| Analyste | Exporter des sessions, une par une | Authorization Code + OIDC | `export:read` | accès 10 min, refresh 8 h avec rotation |
| Job de nuit | Vider le lot, sans personne devant l'écran | Client Credentials | `export:bulk` | accès 15 min, pas de refresh |

`/collect` resterait anonyme : au moment de la collecte, le visiteur n'a pas encore de jeton. L'authentification protège la lecture et l'export. Le navigateur ne peut pas garder un secret, d'où PKCE. Le job de nuit n'a pas d'utilisateur, d'où Client Credentials.

## E5 — Comment SOLO reconnaît un essaim

<a id="e5"></a>

La réputation (niveau 5 du moteur) cherche un même navigateur vu depuis beaucoup d'adresses. Dans `store.ts`, `fingerprintReputation` compte, sur la dernière heure :

```sql
SELECT COUNT(DISTINCT ip) AS d, COUNT(*) AS t
FROM sessions
WHERE canvas_hash IS ? AND webgl_hash IS ? AND ip IS NOT NULL AND created_at >= ?
```

L'identité est le couple `(canvas_hash, webgl_hash)`, pas le canvas seul. Les deux colonnes sont comparées avec `IS`, donc une valeur nulle reste une valeur : un essaim qui omet toujours la même surface se retrouve quand même. Si les deux hashs sont nuls, SOLO ne juge pas : il ne met pas tous les navigateurs durcis dans le même sac.

L'exercice simplifie à `GROUP BY canvas_hash` et `HAVING n >= 10`. Sur la base factice, un canvas est vu depuis **14 IP**. C'est l'essaim. Un humain réutilise peu d'adresses pour une même empreinte. Le bot fait l'inverse : une empreinte, beaucoup d'IP.

Chiffrer `ip` en AES-256-GCM casse ce compte. Le nonce est aléatoire : deux chiffrements de la même adresse sont différents, et `COUNT(DISTINCT ip_enc)` compte des chiffrés, plus des adresses. Sur la base, un second groupe apparaît à 12, qui n'est pas un essaim.

Le blind index `ip_bidx = HMAC(clé, ip)` est déterministe. La même adresse redonne le même index, le compte retrouve les 14, et seulement celles-là. Il révèle encore la fréquence : qui a la colonne voit quelles lignes partagent une IP, sans lire l'adresse. C'est la même pseudonymisation qu'en E2. SOLO, lui, compte aujourd'hui l'IP en clair.

## E6 — Où vivrait une clé maîtresse

<a id="e6"></a>

SOLO ne chiffre pas les colonnes. L'exercice montre comment le faire sans rechiffrer toute la base à chaque rotation.

Une KEK (clé maîtresse) enveloppe une DEK par heure. Les IP de l'heure sont chiffrées avec la DEK. La DEK n'est stockée que chiffrée par la KEK. Sur le jeu du script (6 heures, 4 000 lignes chacune) : réenvelopper les 6 DEK prend **0,03 ms**, rechiffrer les 24 000 lignes prend **62,43 ms**. Détruire la DEK de 11 h rend ces 4 000 lignes illisibles, y compris dans une sauvegarde qui les contient encore. C'est le crypto-shredding : effacer la clé équivaut à effacer les données.

Dans le dépôt, `.gitignore` ignore `.env`, `.env.local` et `certs/*.pem`. `docker-compose.yml` ne pose qu'un chemin de clé TLS (`KEY_PATH=/certs/key.pem`), pas un secret applicatif. La KEK du labo reste en mémoire dans le script. En production elle ne vivrait ni dans le dépôt ni à côté des données : dans un KMS, un HSM ou un coffre (Vault). Le service demande le déchiffrement des DEK, il ne détient pas la clé maîtresse.

## E7 — Combien de temps la visite reste

<a id="e7"></a>

La base légale utilisée par le labo est le consentement (art. 6.1.a) : la collecte ne démarre qu'après la modale. Le destinataire est l'opérateur du labo. Le code n'envoie les données à aucun tiers.

`TTL_MS` vaut une heure. À l'insertion, `expires_at = maintenant + 1 h`. Toutes les cinq minutes, et une fois au démarrage, le sweeper exécute :

```sql
DELETE FROM sessions WHERE expires_at < ?
```

`PRAGMA foreign_keys = ON` est indispensable. Sans lui, SQLite ignore le `ON DELETE CASCADE`, et `client_full` comme `decisions` restent orphelines avec l'empreinte et le verdict. Avec le pragma, la session `001e578b-bdc7-4543-aecc-7998e9306b19` passe de 1 ligne dans chaque fille à 0.

`secure_delete=ON` zéro-ifie les pages libérées du fichier principal. En mode WAL, les anciennes frames (IP, empreintes) resteraient dans le `-wal` jusqu'au checkpoint automatique, bien après l'heure. Le sweeper enchaîne donc avec `wal_checkpoint(TRUNCATE)`.

Trois réductions, que le schéma ne fait pas encore :

1. Tronquer l'IP au `/24` une fois le pays, l'ASN et les drapeaux calculés. Le `/24` garde une géoloc grossière et perd l'abonné. La réputation, si elle doit survivre, passerait par le blind index d'E5.
2. Ne plus recopier dans `client_full` ce qui est déjà en colonnes (`platform`, `canvas_hash`, `webgl_hash`, …). La duplication double ce qu'il faut purger et ce qui fuit.
3. Ne pas garder les IP locales WebRTC. Le score a besoin de savoir qu'une IP locale existe ou non, pas de sa valeur.
