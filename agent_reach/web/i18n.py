# -*- coding: utf-8 -*-
"""Localization helpers for Agent Reach web UI."""

from __future__ import annotations

from typing import Dict

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en", "tr"}

MESSAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "page_title": "Agent Reach Control Deck",
        "hero_title": "Agent Reach Control Deck",
        "hero_body": (
            "Run installation and configuration workflows from a browser while "
            "keeping the original CLI behavior under the hood."
        ),
        "language": "Language",
        "lang_en": "English",
        "lang_tr": "Turkish",
        "doctor_dashboard": "Doctor Dashboard",
        "channels_ready": "channels ready",
        "refresh": "Refresh",
        "install": "Install",
        "configure": "Configure",
        "guided_setup": "Guided Setup",
        "uninstall": "Uninstall",
        "environment": "Environment",
        "proxy_optional": "Proxy (optional)",
        "safe_mode": "safe mode",
        "dry_run": "dry run",
        "refresh_doctor": "refresh doctor",
        "run_install": "Run install",
        "install_output_placeholder": "Install output appears here.",
        "key": "Key",
        "value": "Value",
        "value_placeholder": "Enter value",
        "save_config": "Save config",
        "browser_import": "Cookie import from browser",
        "import_cookies": "Import cookies",
        "configure_output_placeholder": "Configuration output appears here.",
        "ensure_exa": "ensure Exa MCP configured",
        "github_token_optional": "GitHub token (optional)",
        "reddit_proxy_optional": "Reddit proxy (optional)",
        "groq_key_optional": "Groq key (optional)",
        "apply_setup": "Apply setup",
        "setup_output_placeholder": "Guided setup output appears here.",
        "dry_run_first": "dry run first",
        "keep_config": "keep config",
        "run_uninstall": "Run uninstall",
        "uninstall_legend": (
            "Use dry run before destructive operations. Keep-config preserves "
            "local credentials and agent-reach settings."
        ),
        "uninstall_output_placeholder": "Uninstall output appears here.",
        "invalid_env": "Invalid environment value.",
        "unsupported_config_key": "Unsupported config key.",
        "unsupported_browser": "Unsupported browser.",
        "config_value_required": "Configuration value is required.",
        "action_install": "Install",
        "action_configure": "Configure",
        "action_browser_import": "Browser import",
        "action_uninstall": "Uninstall",
        "action_completed": "{action} completed",
        "exit_code": "Exit code",
        "command": "Command",
        "stderr": "stderr",
        "no_stdout": "(no stdout)",
        "guided_setup_result": "Guided setup result",
        "backends": "Backends",
        "not_available": "n/a",
        "status_ok": "Ready",
        "status_warn": "Needs action",
        "status_off": "Disabled",
        "status_error": "Error",
        "status_unknown": "Unknown",
        "tier_0": "Instant channels",
        "tier_1": "Search channels",
        "tier_2": "Advanced channels",
        "setup_saved_github": "GitHub token saved.",
        "setup_saved_proxy": "Reddit and Bilibili proxy saved.",
        "setup_saved_groq": "Groq key saved.",
        "setup_no_change": "No setup value provided. Nothing changed.",
        "exa_missing_mcporter": "mcporter is not installed. Run: npm install -g mcporter",
        "exa_already_configured": "Exa MCP was already configured.",
        "exa_configured": "Exa MCP configured successfully.",
        "exa_setup_failed": "Exa setup failed: {detail}",
    },
    "tr": {
        "page_title": "Agent Reach Kontrol Paneli",
        "hero_title": "Agent Reach Kontrol Paneli",
        "hero_body": (
            "Kurulum ve yapılandırma akışlarını tarayıcıdan çalıştırın; "
            "arka planda mevcut CLI davranışı korunur."
        ),
        "language": "Dil",
        "lang_en": "İngilizce",
        "lang_tr": "Türkçe",
        "doctor_dashboard": "Durum Panosu",
        "channels_ready": "kanal hazır",
        "refresh": "Yenile",
        "install": "Kurulum",
        "configure": "Yapılandırma",
        "guided_setup": "Yönlendirmeli Kurulum",
        "uninstall": "Kaldır",
        "environment": "Ortam",
        "proxy_optional": "Proxy (opsiyonel)",
        "safe_mode": "güvenli mod",
        "dry_run": "önizleme",
        "refresh_doctor": "durumu yenile",
        "run_install": "Kurulumu çalıştır",
        "install_output_placeholder": "Kurulum çıktısı burada görünecek.",
        "key": "Anahtar",
        "value": "Değer",
        "value_placeholder": "Değer girin",
        "save_config": "Yapılandırmayı kaydet",
        "browser_import": "Tarayıcıdan çerez içe aktar",
        "import_cookies": "Çerezleri içe aktar",
        "configure_output_placeholder": "Yapılandırma çıktısı burada görünecek.",
        "ensure_exa": "Exa MCP yapılandırmasını garanti et",
        "github_token_optional": "GitHub token (opsiyonel)",
        "reddit_proxy_optional": "Reddit proxy (opsiyonel)",
        "groq_key_optional": "Groq anahtarı (opsiyonel)",
        "apply_setup": "Kurulumu uygula",
        "setup_output_placeholder": "Kurulum çıktısı burada görünecek.",
        "dry_run_first": "önce önizleme",
        "keep_config": "config dosyasını koru",
        "run_uninstall": "Kaldırmayı çalıştır",
        "uninstall_legend": (
            "Yıkıcı işlemlerden önce önizleme kullanın. keep-config seçeneği "
            "yerel kimlik bilgilerini ve ayarları korur."
        ),
        "uninstall_output_placeholder": "Kaldırma çıktısı burada görünecek.",
        "invalid_env": "Geçersiz ortam değeri.",
        "unsupported_config_key": "Desteklenmeyen yapılandırma anahtarı.",
        "unsupported_browser": "Desteklenmeyen tarayıcı.",
        "config_value_required": "Yapılandırma değeri zorunludur.",
        "action_install": "Kurulum",
        "action_configure": "Yapılandırma",
        "action_browser_import": "Tarayıcı içe aktarma",
        "action_uninstall": "Kaldırma",
        "action_completed": "{action} tamamlandı",
        "exit_code": "Çıkış kodu",
        "command": "Komut",
        "stderr": "hata çıktısı",
        "no_stdout": "(çıktı yok)",
        "guided_setup_result": "Yönlendirmeli kurulum sonucu",
        "backends": "Altyapılar",
        "not_available": "yok",
        "status_ok": "Hazır",
        "status_warn": "Aksiyon gerekli",
        "status_off": "Kapalı",
        "status_error": "Hata",
        "status_unknown": "Bilinmiyor",
        "tier_0": "Anında kullanılabilir",
        "tier_1": "Arama kanalları",
        "tier_2": "Gelişmiş kanallar",
        "setup_saved_github": "GitHub token kaydedildi.",
        "setup_saved_proxy": "Reddit ve Bilibili proxy ayarlandı.",
        "setup_saved_groq": "Groq anahtarı kaydedildi.",
        "setup_no_change": "Kurulum için değer girilmedi. Değişiklik yapılmadı.",
        "exa_missing_mcporter": "mcporter yüklü değil. Çalıştırın: npm install -g mcporter",
        "exa_already_configured": "Exa MCP zaten yapılandırılmış.",
        "exa_configured": "Exa MCP başarıyla yapılandırıldı.",
        "exa_setup_failed": "Exa kurulumu başarısız: {detail}",
    },
}


def normalize_language(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANGUAGE
    normalized = str(lang).strip().lower()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    return DEFAULT_LANGUAGE


def t(lang: str | None, key: str, **kwargs: object) -> str:
    active = normalize_language(lang)
    template = MESSAGES.get(active, {}).get(key) or MESSAGES[DEFAULT_LANGUAGE].get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def status_label(lang: str | None, status: str | None) -> str:
    lookup = {
        "ok": "status_ok",
        "warn": "status_warn",
        "off": "status_off",
        "error": "status_error",
    }
    return t(lang, lookup.get(str(status), "status_unknown"))


def tier_title(lang: str | None, tier: int) -> str:
    return t(lang, f"tier_{tier}")
