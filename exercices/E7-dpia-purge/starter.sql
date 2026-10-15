-- E7 — preuve de purge à 1h (cascade). Lancer :  sqlite3 data/solo_fake.db < starter.sql
-- La cascade n'est active QUE si foreign_keys = ON.
PRAGMA foreign_keys = ON;
.mode box

-- 1) On prend une session au hasard et on note son id.
.print '--- session cible ---'
SELECT id FROM sessions LIMIT 1;

-- 2) Avant : les tables filles ont bien une ligne pour cette session.
.print '--- avant purge : lignes filles (attendu : 1 et 1) ---'
WITH cible AS (SELECT id FROM sessions LIMIT 1)
SELECT
  (SELECT COUNT(*) FROM client_full WHERE session_id = (SELECT id FROM cible)) AS client_full,
  (SELECT COUNT(*) FROM decisions   WHERE session_id = (SELECT id FROM cible)) AS decisions;

-- 3) On force l'expiration de cette session dans le passé...
UPDATE sessions SET expires_at = 0
 WHERE id = (SELECT id FROM sessions LIMIT 1);

-- 4) ...puis on lance le DELETE du sweeper (expires_at < maintenant).
DELETE FROM sessions WHERE expires_at < (strftime('%s','now') * 1000);

-- 5) Après : grâce à ON DELETE CASCADE, les lignes filles ont disparu.
.print '--- apres purge : total orphelins (attendu : 0) ---'
SELECT
  (SELECT COUNT(*) FROM client_full c LEFT JOIN sessions s ON s.id=c.session_id WHERE s.id IS NULL) AS orphelins_client_full,
  (SELECT COUNT(*) FROM decisions   d LEFT JOIN sessions s ON s.id=d.session_id WHERE s.id IS NULL) AS orphelins_decisions;

-- Garde-fou : sans foreign_keys = ON, les orphelins ci-dessus seraient > 0.
