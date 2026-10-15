# E10 — Correction : red-team sur l'instance locale

Cible : `https://localhost:8443` uniquement. Défi 1 : obtenir `clean` avec Playwright, en partant de `../E8-dataset/playwright_bot.py`.

Trois passages. Chaque ligne est une session réelle, verdict lu dans `GET /export/:id`.

| Passage | Verdict | Score | Trust | Signaux |
|---|---|---|---|---|
| Chromium headless, rien de masqué | bot | 1 | 0,3 | `webdriver` `headless_ua` `zero_plugins` `http_inconsistencies` `env_software_gpu` `env_no_hw_video_decode` `env_webgpu_absent` `env_screen_default_dims` `beh_no_interaction` |
| Masques de l'énoncé | suspect | 0,75 | 0,3 | `forged_chrome` `zero_plugins` `env_software_gpu` `env_no_hw_video_decode` `env_webgpu_absent` `beh_mouse_synthetic` |
| Ce que le client déclare, forgé aussi | clean | 0,05 | 0,55 | `env_webgpu_absent` `beh_no_interaction` |

## Ce qui est tombé

Le passage brut est `bot` à 1 à cause de deux signaux durs : `navigator.webdriver === true` et le User-Agent HeadlessChrome. L'écran est `800x600` ou `1280x720` à `devicePixelRatio` 1 (`env_screen_default_dims`). Aucun mouvement (`beh_no_interaction`).

Le second passage fait exactement ce que l'énoncé demande :

- lancement avec `--disable-blink-features=AutomationControlled` et `navigator.webdriver` forcé à `false` ;
- User-Agent Chrome 131 macOS, sans `HeadlessChrome` ;
- viewport 1440×900, écran 1512×982, `devicePixelRatio` 2 ;
- une trentaine de `mouse.move` Playwright et quelques frappes.

`webdriver`, `headless_ua`, `env_screen_default_dims` et `http_inconsistencies` (`missing-accept-language`, parti avec `locale=fr-FR`) disparaissent. Le score passe de 1 à **0,75**, le verdict de `bot` à **`suspect`**. On n'est pas à `clean` : il reste le GPU logiciel SwiftShader (0,65), zéro plugin (0,5), `chrome.runtime` absent (0,15), pas de décodage vidéo matériel, pas de WebGPU, et la souris.

La souris Playwright est elle-même un signal. `mouse.move` avance en ligne droite, la courbure mesurée vaut 0, donc `beh_mouse_synthetic` (0,45) s'ajoute. Bouger « un peu » ne crédite pas un humain si la trajectoire est générée.

Le troisième passage forge le reste de ce que le JavaScript de la page va lire : liste de plugins PDF, `chrome.runtime`, `getParameter` WebGL (le renderer annoncé devient un Apple M1), `decodingInfo` qui répond `powerEfficient: true`. Le verdict tombe à **`clean`, score 0,05**. Les deux signaux encore là pèsent trop peu pour franchir 0,4 : `env_webgpu_absent` (0,1) — `navigator.gpu` existait déjà, le remplacement n'a pas pris — et `beh_no_interaction` (0,2) — les `MouseEvent` dispatchés n'ont pas été comptés. Le crédit de confiance (0,55, plafonné à 0,15 dans le calcul du net) les ramène à 0,05.

## Ce qui a tenu

Le JA4 ne bouge pas de famille. Les trois sessions sont en `t13d1516h2_8daaf6152771_…`, le ClientHello de Chromium headless. Masquer le JavaScript ne le change pas : c'est la pile TLS du process, observée par le serveur avant tout script.

Sur cette version, ce JA4 est classé comme un navigateur. `tls_ua_mismatch` ne part pas, même quand l'UA annonce un Chrome de bureau. L'empreinte est bien enregistrée dans l'export (`server.tls.ja4`), elle ne fait pas basculer le verdict. L'IP est privée : pas de Tor, pas de datacenter, pas de proxy.

Donc, sur cette instance : tout ce qui a fait `bot` puis `suspect` se lisait dans la page, et s'est laissé réécrire. Ce que le serveur voit de lui-même (JA4, en-têtes, IP) est resté vrai, mais aucun de ces signaux n'était assez fort ici pour retenir la session.
