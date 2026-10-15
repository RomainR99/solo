# E4 — Concevoir l'authentification manquante de SOLO (25 min, binômes)

**Objectif.** Choisir le bon mécanisme d'accès pour chaque acteur, sur un cas réel.

## Contexte

SOLO n'a **aucune authentification applicative**. Regarde dans le dépôt :
- `src/server/routes.ts` : `/collect` est ouvert (rate-limit 15/min), `/api/fp/:id` et
  `/export/:id` ne sont protégés que par l'UUID de session dans l'URL.
- `.env.example` : le dit explicitement (« there is currently NO application-level authentication »).

C'est le modèle « URL-capacité » : qui connaît l'URL accède à la donnée.

## Consigne

1. **Risques de l'URL-capacité.** Liste au moins 4 endroits où une URL peut fuiter
   (historique, logs d'un proxy, en-tête `Referer`, capture d'écran partagée…).
2. **Deux acteurs.**
   - le **visiteur** : consulte son propre récap ;
   - l'**analyste data** : exporte des sessions pour entraîner un modèle ;
   - (bonus) le **job d'export** automatisé, chaque nuit.
3. **Un flux par acteur.** Choisis le flux OAuth2/OIDC adapté à chacun et dessine le
   diagramme de séquence (papier ou Mermaid).
4. **Scopes et durées.** Définis les scopes (`fp:read:self`, `export:read`, `export:bulk`)
   et la durée de vie des jetons.

## Livrable

Un diagramme de séquence (papier ou Mermaid) + la liste des scopes et durées.
Le corrigé proposé est dans la slide « E4 · corrigé ».
