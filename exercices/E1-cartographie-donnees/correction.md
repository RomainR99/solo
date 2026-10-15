# E1 — Correction : cartographie des données

Source : le `CREATE TABLE` de `src/server/db.ts`, complété par ce que `src/server/store.ts` écrit vraiment (`writeServerCols`, `writeClientCols`) et par le type `ClientFingerprint` (`src/shared/types.ts`).

SOLO est un labo d'empreinte. La finalité commune de tout le schéma est de **décrire une visite** (pile TLS, HTTP, navigateur, matériel, comportement) pour calculer un verdict bot / humain, puis de **pouvoir filtrer et regrouper** ces visites (`GROUP BY ja3_hash`, `canvas_hash`, etc.). Rétention : 1 h (`TTL_MS` dans `store.ts`), puis purge.

Le schéma est hybride. `sessions` ne garde que les scalaires indexables. Le détail brut part dans des blobs JSON (`server_tls`, `server_http`, `server_ip`, `client_full`, `decisions`), liés par `session_id` avec `ON DELETE CASCADE`.

Légende :

- **Donnée personnelle** : directe (nomme la personne) / indirecte (identifie par recoupement, art. 4 RGPD) / non.
- **Classification** : public / interne / confidentiel / personnelle / sensible (art. 9). Aucune colonne de `sessions` n'est une donnée sensible art. 9.

---

## Tableau — colonnes de `sessions`

| Colonne / blob | Donnée personnelle ? | Classification | Finalité supposée | Risque si fuite |
|---|---|---|---|---|
| `id` | indirecte | personnelle | Clé de la visite ; relie toutes les tables filles | Recoller TLS, HTTP, IP, blob client et verdict d'une même visite |
| `created_at` | indirecte | personnelle | Horodatage de création, base du TTL | Reconstituer quand la personne était en ligne |
| `updated_at` | indirecte | personnelle | Dernière écriture sur la session | Même risque, plus la durée d'activité |
| `expires_at` | non | interne | Échéance de purge (création + 1 h) | Révèle seulement la politique de rétention |
| `server_captured_at` | indirecte | personnelle | Horodatage de la capture TLS/HTTP/IP | Chronologie de la connexion |
| `client_collected_at` | indirecte | personnelle | Horodatage de l'envoi du fingerprint navigateur | Chronologie de la collecte côté client |
| `duration_ms` | indirecte | personnelle | Durée de la fenêtre de collecte | Faible seul ; précise le temps passé sur la page |
| `ip` | **indirecte** | personnelle | Identifiant réseau de la session, entrée de la géoloc et de la réputation | Réidentification via le FAI, corrélation des visites, géoloc approximative |
| `asn` | indirecte | personnelle | Numéro d'opérateur / hébergeur, signal datacenter vs résidentiel | Désigne le FAI ou le cloud, pas la personne seule |
| `asn_org` | indirecte | personnelle | Nom lisible de l'ASN (`Orange`, `Amazon`, …) | Même risque, en clair |
| `country` | indirecte | personnelle | Pays déduit de l'IP (GeoIP) | Localisation grossière |
| `is_datacenter` | indirecte | personnelle | Drapeau « IP d'hébergeur » pour le score | Qualifie le type de connexion de la personne |
| `is_proxy_hint` | indirecte | personnelle | Drapeau proxy / VPN | Révèle un contournement (VPN, proxy) |
| `reverse_dns` | indirecte | personnelle | Nom PTR de l'IP (souvent le FAI, parfois un hostname client) | Peut contenir un indice d'abonné |
| `is_tor_exit` | indirecte | personnelle | Drapeau nœud de sortie Tor | Révèle l'usage de Tor |
| `tcp_rtt_ms` | indirecte | interne | Latence TCP, signal de distance / chemin réseau | Faible ; donne un ordre de grandeur de distance |
| `ja3` | indirecte | personnelle | Chaîne JA3 brute (ciphers, extensions, courbes du ClientHello) | Regroupe toutes les visites de la même pile TLS |
| `ja3_hash` | indirecte | personnelle | Condensé du JA3, indexé pour les `GROUP BY` | Même pouvoir de regroupement, plus court à corréler |
| `ja4` | indirecte | personnelle | Empreinte TLS plus récente, elle aussi indexée | Même nature que `ja3_hash` |
| `tls_version` | non | interne | Version TLS négociée | Caractéristique de protocole, partagée par des millions de clients |
| `sni` | non | interne | Nom d'hôte demandé dans le ClientHello (le labo lui-même) | Révèle le site visité, ici le labo, pas l'identité du visiteur |
| `alpn` | non | interne | Protocoles proposés (`h2`, `http/1.1`) | Caractéristique de pile, très partagée |
| `user_agent` | indirecte | personnelle | Navigateur, OS et parfois appareil, lus dans l'en-tête HTTP | Forte composante d'empreinte ; versions logicielles exploitables |
| `http_version` | non | interne | Version HTTP de la requête | Protocole, non identifiant seul |
| `accept_language` | indirecte | personnelle | Langues préférées annoncées par le navigateur | Inférence de langue / pays ; entre dans l'empreinte |
| `sec_fetch_site` | non | interne | Contexte Fetch (`same-origin`, `cross-site`, …) | Dit d'où vient la navigation, sans nommer la personne |
| `sec_fetch_mode` | non | interne | Mode Fetch (`navigate`, `cors`, …) | Métadonnée de requête |
| `sec_fetch_dest` | non | interne | Destination Fetch (`document`, `empty`, …) | Métadonnée de requête |
| `sec_fetch_user` | non | interne | Présence d'une activation utilisateur (`?1`) | Signal technique, pas un identifiant |
| `platform` | indirecte | personnelle | `navigator.platform` (`MacIntel`, `Win32`, …) | Famille d'OS, brique d'empreinte |
| `vendor` | non | interne | Éditeur du navigateur (`Google Inc.`, `Apple`, …) | Très partagé |
| `language` | indirecte | personnelle | `navigator.language` | Même risque que `accept_language` |
| `timezone` | indirecte | personnelle | Fuseau IANA (`Europe/Paris`) | Pays ou région ; incohérence avec l'IP = signal de VPN |
| `screen_w` | indirecte | personnelle | Largeur d'écran | Brique d'empreinte, peu unique seule |
| `screen_h` | indirecte | personnelle | Hauteur d'écran | Idem |
| `dpr` | indirecte | personnelle | Densité de pixels | Distingue mobile / retina, brique d'empreinte |
| `webdriver` | non | interne | Drapeau d'automatisation (`navigator.webdriver`) | Dit si un robot pilote le navigateur, pas qui est la personne |
| `canvas_hash` | indirecte | personnelle | Hash du rendu canvas, indexé pour la réputation | Quasi-identifiant d'appareil une fois combiné |
| `webgl_hash` | indirecte | personnelle | Hash des paramètres WebGL, indexé avec le canvas | Idem, très stable sur une même machine |
| `webgl_renderer` | indirecte | personnelle | GPU en clair (`Apple M1`, `NVIDIA GeForce…`) | Modèle matériel lisible, plus parlant que le hash |
| `audio_hash` | indirecte | personnelle | Hash de l'oscillateur AudioContext | Autre brique d'empreinte matériel / OS |
| `fonts_count` | indirecte | interne | Nombre de polices détectées (pas la liste) | Faible seul ; la liste, elle, est dans le blob |
| `verdict` | indirecte | confidentiel | Synthèse du moteur (`clean`, `bot`, …), indexée | Étiquette une visite, donc une personne |
| `bot_score` | indirecte | confidentiel | Score numérique du même moteur | Profilage ; permet de trier les personnes |
| `trust_score` | indirecte | confidentiel | Score de confiance complémentaire | Idem |
| `decision_forced` | non | interne | Indique si le verdict a été forcé | Métadonnée du moteur, pas de la personne |
| `decision_version` | non | interne | Version de config du moteur (`2026.06.8`) | Aucun lien avec une personne |
| **blob `client_full`** | indirecte (et, dedans, IP locales quasi directes) | personnelle | Copie JSON intégrale du fingerprint navigateur, pour réafficher le détail que les colonnes ne portent pas | Cumule empreinte, IP locales WebRTC, liste de polices, voix, et le comportement ; une fuite vaut toute la visite |

Les scores et le verdict sont classés **confidentiel** plutôt que « personnelle » : ce sont des jugements produits par le labo sur la visite, plus sensibles à la fuite qu'un simple fuseau horaire, sans être pour autant des données art. 9.

---

## 1. `ip` : personnelle, indirecte

`ip` est une donnée personnelle **indirecte**.

Elle ne nomme personne (ce n'est pas une donnée directe, au sens d'un nom ou d'un e-mail). Elle identifie pourtant une personne physique au sens de l'art. 4 : l'arrêt *Breyer* (CJUE, C-582/14) considère qu'une adresse IP dynamique est personnelle pour l'éditeur du site, parce qu'avec des moyens raisonnables — typiquement le FAI — on peut remonter à l'abonné.

Dans SOLO elle est en clair, indexée (`idx_sessions_ip`), et recopiée dans le blob `server_ip`. C'est l'identifiant réseau de la session : géoloc, ASN, Tor, proxy et réputation s'appuient dessus.

Nuance utile en binôme : une IP partagée (NAT d'entreprise, CGNAT) désigne souvent un foyer ou un réseau, pas un individu seul. Elle reste personnelle. Une IPv6 stable ou une IP fixe se rapproche d'un identifiant durable.

---

## 2. Pourquoi `canvas_hash`, `webgl_hash` et `ja3_hash` sont des identifiants

Un identifiant RGPD n'a pas besoin de contenir un nom. L'art. 4 vise aussi les identifiants en ligne et tout élément qui permet de **singulariser** quelqu'un, seul ou par croisement.

Ces trois colonnes sont des condensés stables, calculés pour être comparés d'une visite à l'autre (d'où les index) :

- `canvas_hash` et `webgl_hash` viennent du rendu graphique du navigateur (GPU, pilote, OS, polices). Deux machines différentes produisent en pratique des hashs différents. Combinés l'un à l'autre — c'est exactement ce que fait `fingerprintReputation` dans `store.ts` — ils rapprochent toutes les visites d'un même poste, sans jamais avoir lu un nom.
- `ja3_hash` condense le ClientHello TLS (suites de chiffrement, extensions, courbes). Il identifie une **pile** (Chrome sur Windows, Firefox, une lib Python…) partagée par beaucoup de gens. Seul, il est peu unique. Croisé avec l'IP, le user-agent ou le canvas, il relie des sessions et détecte un client qui n'est pas un navigateur grand public.

Ce ne sont pas des données sensibles art. 9. Le canvas et le WebGL décrivent la machine et le logiciel, pas un trait biométrique du corps. Le risque est le pistage, pas la catégorie particulière.

---

## 3. Ce qui est stocké du clavier

Le client n'enregistre pas le caractère frappé.

Dans `src/client/behavioral/keyboard.ts`, chaque événement garde `e.code` (la **position physique** : `KeyA`, `Backspace`, `Space`) et l'instant `t`. Le commentaire du fichier est explicite : `e.key` n'est jamais lu, donc le caractère produit — y compris un mot de passe — n'est ni capturé ni envoyé.

Et même ce `code` ne va pas en base. `keyboardAggregate` (`src/client/behavioral/aggregate.ts`) ne sert les codes qu'en mémoire, pour apparier keydown / keyup et compter les retours arrière. Le JSON envoyé, puis stocké dans `client_full.behavioral.keyboard`, ne contient que des compteurs et des moyennes :

- `keydowns`, `keyups`
- `meanDwellMs`, `stdDwellMs` (temps d'enfoncement)
- `meanFlightMs`, `stdFlightMs` (temps entre deux touches)
- `backspaceRatio`

Il n'y a pas de colonne clavier dans `sessions`. Rien de tout cela n'est une donnée art. 9 : ce n'est pas un gabarit biométrique, seulement un rythme agrégé pour distinguer un humain d'un script.

---

## 4. Ce que `client_full` duplique — et ce qu'il ajoute

`writeClientCols` fait deux écritures du **même** objet `ClientFingerprint` :

1. une projection de quelques champs dans les colonnes de `sessions` ;
2. `JSON.stringify(client)` intégral dans `client_full.data`.

Les colonnes suivantes sont donc **en double** (colonne indexable + même valeur dans le JSON) :

| Colonne `sessions` | Champ dans le blob |
|---|---|
| `client_collected_at` | `collectedAt` |
| `duration_ms` | `durationMs` |
| `platform`, `vendor`, `language` | `navigator.platform`, `.vendor`, `.language` |
| `timezone` | `locale.timezone` |
| `screen_w`, `screen_h`, `dpr` | `screen.width`, `.height`, `.devicePixelRatio` |
| `webdriver` | `automation.webdriver` |
| `canvas_hash` | `canvas.dataUrlHash` |
| `webgl_hash` | `webgl.parametersHash` |
| `webgl_renderer` | `webgl.unmaskedRenderer` (sinon `renderer`) |
| `audio_hash` | `audio.oscillatorHash` |
| `fonts_count` | `fonts.detectedFonts.length` |

Le blob **ne duplique pas** les colonnes serveur (`ip`, `ja3`, `ja3_hash`, `user_agent` HTTP, `verdict`, …). Celles-là ont leurs propres blobs : `server_ip`, `server_tls`, `server_http`, `decisions`.

Tout le reste n'existe **que** dans `client_full`. C'est souvent plus identifiant que les colonnes :

- le navigateur complet (`userAgent`, `languages`, `hardwareConcurrency`, `deviceMemory`, `uaData` avec modèle et architecture) ;
- l'écran complet et le détail de locale (formats de date et de nombre) ;
- la **liste** des polices, pas seulement le compte ;
- WebRTC : `localIps`, `publicIp`, candidats ICE — les IP de la machine et du réseau local ;
- voix TTS, hash des périphériques média, adaptateur WebGPU ;
- préférences CSS (`prefers-reduced-motion`, contraste), qui peuvent faire inférer un handicap sans être pour autant stockées comme donnée de santé ;
- l'agrégat comportemental (souris, clavier, scroll, touch).

Conséquence pour la suite (E7) : purger `sessions` ne suffit pas si les filles ne partent pas avec. Le `ON DELETE CASCADE` de `db.ts` est là pour ça, et la duplication dans `client_full` est une piste de minimisation — ne pas recopier dans le blob ce qui est déjà en colonnes, et ne pas garder les IP locales WebRTC.

## `colonne` dans `reputation`

`colonne` est le paramètre de `reputation`. C'est le nom de la colonne de la table `sessions` dont on compte les valeurs différentes, pour un même `canvas_hash`.

Le script l'appelle trois fois, avec trois colonnes :

- `"ip"` : l'adresse en clair. Quatorze adresses différentes pour le même canvas.
- `"ip_enc"` : la même adresse chiffrée. Chaque ligne a un chiffré différent, donc le compte ne suit plus les adresses.
- `"ip_bidx"` : l'index HMAC. La même adresse redonne la même valeur, et on retrouve les quatorze.

`canvas_hash` ne change pas d'un appel à l'autre. Seule la colonne comptée change.
