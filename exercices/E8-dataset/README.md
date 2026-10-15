# E8 — Constituer un dataset face à SOLO (25 min, groupes de 3–4)

**Objectif.** Produire des sessions variées et observer ce que SOLO en déduit.
**Prérequis : SOLO lancé en local** (`docker compose up -d --build`, `https://localhost:8443`).

> ⚠️ En local, SOLO ne voit qu'une IP privée : les signaux IP (datacenter, proxy, Tor) **ne se
> déclenchent pas**. C'est normal et c'est le sujet de la discussion — seuls les signaux TLS,
> navigateur et comportement jouent ici.

## Produire au moins 6 sessions

| Client | Comment | Verdict attendu (à vérifier) |
|---|---|---|
| Chrome, interaction normale | ouvrir la page, bouger/taper/scroller 8 s | `clean` |
| Firefox ou Safari | idem | `clean` |
| Navigateur, **sans** interaction | ouvrir et ne rien toucher | `clean` ou `suspect` |
| `curl` | `curl -k https://localhost:8443/api/fp/me` | incohérence TLS↔UA |
| Python `requests` + UA Chrome | GET avec `User-Agent` de Chrome | `tls_ua_mismatch` |
| Playwright headless | `python3 playwright_bot.py` (fourni) | `bot` (signal dur N1) |

Pour chaque session via navigateur, récupère l'export :
`curl -k https://localhost:8443/export/<id> -o session.json`.

## Fichier fourni

- `playwright_bot.py` : ouvre SOLO en headless et déclenche une session « bot ».
  Installer d'abord : `pip install playwright && playwright install chromium`.

## Livrable

Un **CSV commun à la promo** (un dossier partagé), une ligne par session :
`client, ja4, verdict, bot_score, trust_score, signaux`.
On s'en sert directement en E9. Modèle de colonnes dans `dataset_modele.csv`.
