# E7 — Correction : mini-DPIA et preuve de purge

Reprise du tableau d'E1. La collecte est derrière la modale de consentement : la base légale est le consentement (art. 6.1.a). La durée est la même pour tout le schéma : **1 h** (`TTL_MS` dans `store.ts`), puis `DELETE FROM sessions WHERE expires_at < now`. Les tables filles partent avec, si `PRAGMA foreign_keys = ON`. Le destinataire effectif est l'opérateur du labo. Le code n'envoie les données à aucun tiers.

## Partie 1 — Mini-DPIA

| Donnée | Base légale | Durée | Destinataires | Mesure existante | Mesure à ajouter |
|---|---|---|---|---|---|
| `id` | Consentement | 1 h | Opérateur du labo | UUID v4 imprévisible, généré serveur | Ne plus s'en servir comme clé d'accès dans l'URL (E4) |
| `created_at`, `updated_at`, `server_captured_at`, `client_collected_at`, `duration_ms` | Consentement | 1 h | Opérateur du labo | Purge avec la session | Rien de plus : ce sont des métadonnées de la visite |
| `expires_at` | Non personnelle | 1 h | Opérateur du labo | Sert justement à déclencher la purge | — |
| `ip` | Consentement | 1 h | Opérateur du labo | En clair, indexée ; `secure_delete` à la purge | Tronquer au `/24` après la géoloc ; blind index si la réputation doit survivre (E5) |
| `asn`, `asn_org`, `country`, `is_datacenter`, `is_proxy_hint`, `reverse_dns`, `is_tor_exit` | Consentement | 1 h | Opérateur du labo | Déduits de l'IP, purgés avec elle | Les garder, eux, après avoir jeté l'IP précise |
| `tcp_rtt_ms` | Consentement | 1 h | Opérateur du labo | Purge avec la session | — |
| `ja3`, `ja3_hash`, `ja4` | Consentement | 1 h | Opérateur du labo | Indexés pour le regroupement | Ne conserver que le hash, pas la chaîne `ja3` brute |
| `tls_version`, `sni`, `alpn`, `http_version`, `sec_fetch_*` | Non personnelles | 1 h | Opérateur du labo | Purge avec la session | — |
| `user_agent`, `accept_language`, `language`, `platform`, `timezone`, `screen_w`, `screen_h`, `dpr` | Consentement | 1 h | Opérateur du labo | Scalaires indexables, purgés avec la session | Ne pas les recopier dans `client_full` |
| `vendor`, `webdriver`, `fonts_count`, `decision_forced`, `decision_version` | Non personnelles ou très faibles | 1 h | Opérateur du labo | Purge avec la session | — |
| `canvas_hash`, `webgl_hash`, `webgl_renderer`, `audio_hash` | Consentement | 1 h | Opérateur du labo | Indexés ; la réputation ne compte que dans la fenêtre d'1 h | Hasher le renderer en clair ; ne pas dupliquer les hashs dans le blob |
| `verdict`, `bot_score`, `trust_score` | Consentement | 1 h | Opérateur du labo | Synthèse en colonnes, détail JSON dans `decisions`, cascade | Réserver la lecture à un jeton `export:read` (E4) |
| Blob `client_full` | Consentement | 1 h | Opérateur du labo | `ON DELETE CASCADE`, `secure_delete` | Ne plus y mettre les colonnes déjà dans `sessions` ; ne pas y garder les IP locales WebRTC |
| Blob `decisions` | Consentement | 1 h | Opérateur du labo | Cascade sur `session_id` | Même contrôle d'accès que le verdict |

## Trois mesures de minimisation

1. **Tronquer l'IP au `/24` après l'enrichissement.** Le pays, l'ASN et les drapeaux datacenter / proxy / Tor sont déjà calculés. L'adresse complète ne sert plus qu'à réidentifier. Un `/24` garde une géoloc grossière et perd l'abonné.
2. **Ne pas dupliquer les colonnes dans `client_full`.** `platform`, `timezone`, `canvas_hash`, `webgl_hash`, `audio_hash`, `fonts_count` et les autres scalaires sont déjà dans `sessions`. Les réécrire dans le JSON double la donnée à purger et à faire fuiter.
3. **Ne pas conserver les IP locales WebRTC.** `client_full.webrtc.localIps` (et `publicIp`) désignent la machine et le réseau local. Le score n'a besoin que du fait qu'une IP locale existe ou non, pas de sa valeur.

## Partie 2 — Preuve de purge

```bash
sqlite3 data/solo_fake.db < starter.sql
```

`starter.sql` commence par `PRAGMA foreign_keys = ON`. Sans ça, SQLite ignore le `ON DELETE CASCADE` de `client_full` et `decisions`.

```text
--- session cible ---
┌──────────────────────────────────────┐
│                  id                  │
├──────────────────────────────────────┤
│ 001e578b-bdc7-4543-aecc-7998e9306b19 │
└──────────────────────────────────────┘
--- avant purge : lignes filles (attendu : 1 et 1) ---
┌─────────────┬───────────┐
│ client_full │ decisions │
├─────────────┼───────────┤
│ 1           │ 1         │
└─────────────┴───────────┘
--- apres purge : total orphelins (attendu : 0) ---
┌───────────────────────┬─────────────────────┐
│ orphelins_client_full │ orphelins_decisions │
├───────────────────────┼─────────────────────┤
│ 0                     │ 0                   │
└───────────────────────┴─────────────────────┘
```

Avant le `DELETE`, la session `001e578b-bdc7-4543-aecc-7998e9306b19` avait une ligne dans `client_full` et une ligne dans `decisions`. Le script met son `expires_at` à 0, puis exécute le même `DELETE` que le sweeper : `expires_at < maintenant`.

Dans cette copie, les 482 sessions étaient déjà au-delà d'une heure (`expires_at` max. `1792014120419`, instant du test `1792097587000`). Le `DELETE` les a donc toutes retirées, pas seulement la session forcée. Après coup : 0 session, 0 ligne dans `client_full`, 0 ligne dans `decisions`, et **0 orphelin** dans les deux tables filles. Les filles sont parties avec le parent. Si `foreign_keys` avait été laissé à `OFF`, ces lignes filles seraient restées.
