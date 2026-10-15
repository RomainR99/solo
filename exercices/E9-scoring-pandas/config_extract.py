# -*- coding: utf-8 -*-
"""Poids et seuils extraits de src/shared/decision/config.ts (n1n2n3n4n5-trust-2026.06.8).
Ne pas inventer : ces valeurs sont copiées du code de SOLO."""

# Signaux "durs" : présence seule -> bot forcé, score 1 (niveau 1 uniquement).
HARD_SIGNALS = {"webdriver", "pw_globals", "cdp_traces", "selenium", "phantom",
                "nightmare", "headless_ua"}

# Poids des signaux "mous", par niveau.
WEIGHTS = {
    1: {"forged_chrome": 0.15, "zero_plugins": 0.5, "notif_no_focus": 0.15},
    2: {"tls_ua_mismatch": 0.7, "http_inconsistencies": 0.5, "ip_tor": 0.6,
        "ip_datacenter": 0.4, "ip_proxy": 0.4, "rdns_hosting": 0.25, "rtt_incoherence": 0.3,
        "lang_header_js_mismatch": 0.5, "client_hints_ua_mismatch": 0.5},
    3: {"env_platform_os_mismatch": 0.6, "env_languages_empty": 0.5, "env_uadata_incoherent": 0.3,
        "env_software_gpu": 0.65, "env_render_surfaces_absent": 0.5, "env_render_hashes_absent": 0.2,
        "env_fonts_minimal": 0.3, "env_no_hw_video_decode": 0.15, "env_speech_no_voices": 0.2,
        "env_no_media_devices": 0.25, "env_webgpu_absent": 0.1, "env_screen_default_dims": 0.3,
        "env_permissions_all_denied": 0.15, "env_locale_ip_mismatch": 0.2,
        "env_engine_ua_mismatch": 0.65, "env_webrtc_no_local_ip": 0.15, "env_vm_resource_profile": 0.25},
    4: {"beh_no_interaction": 0.2, "beh_mouse_synthetic": 0.45, "beh_mouse_constant_speed": 0.3,
        "beh_scroll_linear": 0.4, "beh_keystroke_robotic": 0.45},
    5: {"rep_fp_many_ips": 0.6, "rep_fp_swarm": 0.4},
}

# Seuils d'agrégation appliqués au score net.
BLOCK = 0.8      # net >= 0.8 -> bot
REVIEW = 0.4     # net >= 0.4 -> suspect ; sinon clean
MAX_FORGEABLE_OFFSET = 0.15   # plafond de la part forgeable du crédit de confiance

# Niveau de chaque signal (pour retrouver à quel niveau additionner).
LEVEL_OF = {s: lvl for lvl, d in WEIGHTS.items() for s in d}
