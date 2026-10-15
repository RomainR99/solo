#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E8 — génère une session « bot » contre SA PROPRE instance SOLO (localhost).

Prérequis :
    pip install playwright
    playwright install chromium

Usage :
    python3 playwright_bot.py [https://localhost:8443]

À n'utiliser QUE sur sa propre instance locale. Jamais sur un site tiers (art. 323-1 CP).
"""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://localhost:8443"


def main():
    with sync_playwright() as p:
        # headless = navigator.webdriver true + pas de vraies interactions
        # => SOLO doit lever un signal dur N1 (webdriver / headless) -> verdict bot.
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(ignore_https_errors=True)   # cert auto-signé
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle")
        print("webdriver vu par la page :", page.evaluate("navigator.webdriver"))
        # on laisse la collecte se faire (~8 s) sans interaction humaine
        page.wait_for_timeout(9000)
        # selon ta version de SOLO, le verdict s'affiche sur le récap :
        try:
            print("contenu visible :", page.inner_text("body")[:300])
        except Exception:
            pass
        browser.close()
    print("\\nRécupère l'export de cette session : curl -k %s/export/<id> -o bot.json" % URL)


if __name__ == "__main__":
    main()
