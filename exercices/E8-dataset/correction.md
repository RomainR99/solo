# E8 — Correction : dataset face à SOLO local

SOLO tournait sur `https://localhost:8443`. L'IP vue par le serveur est privée : aucun signal datacenter, proxy ou Tor, comme le dit l'énoncé. Seuls le TLS, le navigateur et le comportement comptent.

Firefox n'est pas installé sur la machine. La ligne Firefox est celle de Firefox 157 lancé par Playwright. Chrome est Google Chrome lancé par Playwright, en headless : le User-Agent contient donc HeadlessChrome.

Le CSV est `dataset.csv`.

| Client | JA4 | Verdict | bot | trust | Signaux |
|---|---|---|---|---|---|
| chrome-interaction | `t13d1517h2_8daaf6152771_43736b97bd57` | bot | 1 | 1 | `webdriver` `headless_ua` `env_screen_default_dims` |
| firefox-interaction | `t13d1517h2_8daaf6152771_3cbfd9057e0d` | bot | 1 | 0.65 | `webdriver` |
| chrome-sans-interaction | `t13d1517h2_8daaf6152771_43736b97bd57` | bot | 1 | 0.55 | `webdriver` `headless_ua` `env_screen_default_dims` `beh_no_interaction` |
| curl | `t13d4907h2_0d8feac7bc37_7395dae3b2f3` | clean | 0.35 | 1 | `http_inconsistencies` `env_screen_default_dims` |
| python-requests-ua-chrome | `t13d1812h1_85036bcba153_b26ce05bbdd6` | bot | 0.85 | 1 | `tls_ua_mismatch` `http_inconsistencies` `env_screen_default_dims` |
| playwright-headless | `t13d1516h2_8daaf6152771_a12e6946bbe1` | bot | 1 | 0.3 | `webdriver` `headless_ua` `zero_plugins` `http_inconsistencies` `env_software_gpu` `env_no_hw_video_decode` `env_webgpu_absent` `env_screen_default_dims` `beh_no_interaction` |

## Ce que SOLO en déduit

Le modèle du dossier attendait `clean` pour un Chrome ou un Firefox qu'on manipule à la main. Ici les deux sont `bot`, score 1. Playwright pose `navigator.webdriver = true`. C'est un signal dur N1 (`webdriver` dans `hardSignals`) : le verdict est forcé, les 40 événements de souris et de clavier du Chrome n'y changent rien. Le Chrome headless ajoute `headless_ua`.

Sans interaction, le même Chrome ajoute `beh_no_interaction` (0 événement). Le score reste 1 à cause de `webdriver`. Le trust baisse (1 → 0,55) parce que le comportement ne crédite plus rien.

Le headless Playwright sans le canal Chrome accumule les signaux d'environnement : GPU logiciel, pas de décodage vidéo matériel, pas de WebGPU, zéro plugin, écran par défaut. Le trust tombe à 0,3. Le verdict est déjà `bot` dès `webdriver`.

`curl -k https://localhost:8443/api/fp/me` ne crée pas de session : la route renvoie seulement le TLS vu sur cette connexion. Son JA4 est `t13d4907h2_0d8feac7bc37_7395dae3b2f3`. Pour avoir un verdict, le même client a envoyé un `POST /collect` dont le corps annonce un Chrome normal (`webdriver` faux, UA sans Headless). SOLO ne lève pas `tls_ua_mismatch` : le ClientHello de curl est classé comme un navigateur. Il lève `http_inconsistencies`. Le trust à 1 ramène le verdict à `clean` (score 0,35). L'incohérence TLS↔UA attendue par le modèle n'est pas celle de curl, sur cette version.

`requests` avec le même corps et un User-Agent Chrome a un autre JA4, `t13d1812h1_85036bcba153_b26ce05bbdd6`. Là, `tls_ua_mismatch` part : la pile TLS n'est pas celle d'un Chrome, alors que l'UA en annonce un. Verdict `bot`, score 0,85. C'est le cas que l'énoncé vise pour la ligne Python.
