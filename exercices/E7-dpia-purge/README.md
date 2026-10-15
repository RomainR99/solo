# E7 — Mini-DPIA de SOLO + preuve de purge (25 min, binômes)

**Objectif.** Formaliser l'analyse d'impact et **prouver** que la rétention d'1h efface bien
tout, tables filles comprises.

## Fichiers

- `data/solo_fake.db` : copie de la base d'E5 (schéma réel, tables `sessions`, `client_full`,
  `decisions` avec `ON DELETE CASCADE`).
- `starter.sql` : requêtes de preuve de purge.

## Partie 1 — Mini-DPIA (papier / tableur)

Reprends le tableau d'**E1** et ajoute, pour chaque donnée :
base légale · durée de conservation · destinataires · mesure de sécurité existante · mesure à ajouter.

Puis, trois mesures de **minimisation** concrètes sur le schéma de SOLO. Pistes :
- tronquer l'IP au `/24` après enrichissement (garde la géoloc, perd l'identifiant précis) ;
- ne pas dupliquer les colonnes dans `client_full` ;
- ne pas conserver les IP locales WebRTC.

## Partie 2 — Preuve de purge (SQL)

Avec `sqlite3 data/solo_fake.db` et `starter.sql` :

1. Vérifie que `PRAGMA foreign_keys = ON` (sinon la cascade est ignorée).
2. Prends une session, force son `expires_at` dans le passé, lance le `DELETE` du sweeper.
3. Vérifie que les lignes correspondantes dans `client_full` **et** `decisions` ont disparu.

```bash
sqlite3 data/solo_fake.db < starter.sql
```

## Livrable

Le tableau DPIA complété + la sortie SQL montrant 0 ligne orpheline dans les tables filles.
