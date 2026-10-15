# E1 — Cartographier les données de SOLO (25 min, binômes)

**Objectif.** Savoir repérer une donnée personnelle et la classer, sur un vrai schéma.

## Support

Le bloc `CREATE TABLE` de `src/server/db.ts` dans le dépôt SOLO (6 tables :
`sessions`, `server_tls`, `server_http`, `server_ip`, `client_full`, `decisions`).
Ouvre ce fichier et regarde surtout la table `sessions` et le blob `client_full`.

## Consigne

Pour chaque colonne de `sessions` (et pour le blob `client_full`), remplis une ligne :

| Colonne / blob | Donnée personnelle ? (directe / indirecte / non) | Classification | Finalité supposée | Risque si fuite |
|---|---|---|---|---|

Classification : public / interne / confidentiel / personnelle / sensible (art. 9 RGPD).

## Questions à trancher en binôme

1. `ip` : donnée personnelle ou pas ? Directe ou indirecte ?
2. `canvas_hash`, `webgl_hash`, `ja3_hash` : en quoi sont-ils identifiants, alors qu'ils ne
   contiennent ni nom ni email ?
3. Qu'est-ce qui est stocké du **clavier** ? (indice : cherche `e.code` vs `e.key` dans
   `src/client/behavioral/keyboard.ts`)
4. Le blob `client_full` : que duplique-t-il par rapport aux colonnes de `sessions` ?

## Livrable

Le tableau rempli. On le **réutilise tel quel en E7** pour la mini-DPIA.
