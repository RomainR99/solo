# E10 — Red-team express (20 min, groupes)

**Objectif.** Toucher du doigt ce qui se forge et ce qui résiste, en essayant de tromper SOLO.

> ⚠️ **Charte.** Uniquement sur **votre propre instance** (`https://localhost:8443`).
> Jamais sur un site tiers. L'accès frauduleux à un système est puni par l'art. 323-1 du Code pénal.

## Un défi au choix (sur votre instance locale)

1. **Obtenir `clean` avec Playwright.** À partir de `../E8-dataset/playwright_bot.py`, essayez de
   faire baisser le score : masquer `navigator.webdriver`, mettre un `User-Agent` crédible, fixer
   une taille d'écran réaliste, ajouter quelques mouvements de souris. Jusqu'où descendez-vous ?
   Qu'est-ce qui **reste** (l'empreinte TLS de Chromium headless, l'absence de comportement humain) ?

2. **Forger un payload `/collect` à la main.** Avec `curl`/Python, envoyez un corps JSON inventé à
   `/collect` et regardez quels signaux tombent. Lesquels ne pouvez-vous **pas** fabriquer
   (ceux que le serveur observe lui-même : empreinte TLS, IP, timing) ?

3. **Trouver un faux positif.** Faites classer `suspect` un **vrai humain** : via un VPN, un
   navigateur durci (Tor Browser, Brave en mode strict), une extension anti-fingerprint.
   Quel signal l'a fait basculer ?

## Restitution

2 minutes par groupe : **ce qui est tombé, ce qui a tenu**. Puis 5 minutes de questions sur l'examen.

## Idée clé à faire ressortir

Tout ce que le **client déclare** (le JavaScript) se forge. Ce que le **serveur observe**
(TLS, IP, réputation) est bien plus dur à falsifier. C'est là-dessus que repose un anti-bot sérieux.
