# -*- coding: utf-8 -*-
"""Local web UI for Agent Reach."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from agent_reach.config import Config
from agent_reach.core import AgentReach
from agent_reach.web.i18n import (
    DEFAULT_LANGUAGE,
    normalize_language,
    status_label as _status_label,
    t as _t,
    tier_title as _tier_title,
)

ALLOWED_CLI_COMMANDS = {"doctor", "install", "configure", "uninstall"}
ALLOWED_CONFIG_KEYS = {
    "proxy",
    "github-token",
    "groq-key",
    "twitter-cookies",
    "youtube-cookies",
    "xhs-cookies",
}
ALLOWED_BROWSERS = {"chrome", "firefox", "edge", "brave", "opera"}

STATUS_LABEL = {
    "ok": "Ready",
    "warn": "Needs action",
    "off": "Disabled",
    "error": "Error",
}

STATUS_CLASS = {
    "ok": "status-ok",
    "warn": "status-warn",
    "off": "status-off",
    "error": "status-error",
}


@dataclass
class CommandResult:
    command: str
    return_code: int
    stdout: str
    stderr: str


SENSITIVE_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"(gho_)[A-Za-z0-9_]+", r"\\1***"),
    (r"(gsk_)[A-Za-z0-9_]+", r"\\1***"),
    (r"(auth_token=)[^;\\s]+", r"\\1***"),
    (r"(ct0=)[^;\\s]+", r"\\1***"),
    (r"(github-token\s+)[^\\s]+", r"\\1***"),
    (r"(groq-key\s+)[^\\s]+", r"\\1***"),
    (r"(twitter-cookies\s+)[^\\n]+", r"\\1***"),
)


def create_app() -> FastAPI:
    app = FastAPI(title="Agent Reach UI", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def index(lang: str = Query(DEFAULT_LANGUAGE)) -> HTMLResponse:
        active_lang = normalize_language(lang)
        results = AgentReach().doctor()
        return HTMLResponse(_render_page(results, active_lang))

    @app.get("/api/doctor")
    def doctor_json() -> JSONResponse:
        return JSONResponse(AgentReach().doctor())

    @app.get("/ui/doctor", response_class=HTMLResponse)
    def doctor_fragment(lang: str = Query(DEFAULT_LANGUAGE)) -> HTMLResponse:
        active_lang = normalize_language(lang)
        return HTMLResponse(_render_doctor_panel(AgentReach().doctor(), active_lang))

    @app.post("/ui/actions/install", response_class=HTMLResponse)
    def run_install(
        env: str = Form("auto"),
        proxy: str = Form(""),
        safe: Optional[str] = Form(None),
        dry_run: Optional[str] = Form(None),
        refresh_doctor: Optional[str] = Form(None),
        lang: str = Form(DEFAULT_LANGUAGE),
    ) -> HTMLResponse:
        active_lang = normalize_language(lang)
        if env not in {"local", "server", "auto"}:
            raise HTTPException(status_code=400, detail=_t(active_lang, "invalid_env"))

        args = ["install", f"--env={env}"]
        if proxy.strip():
            args.extend(["--proxy", proxy.strip()])
        if safe is not None:
            args.append("--safe")
        if dry_run is not None:
            args.append("--dry-run")

        result = _run_cli(args)
        body = _render_command_result(_t(active_lang, "action_install"), result, active_lang)
        if refresh_doctor is not None:
            body += _render_doctor_oob(active_lang)
        return HTMLResponse(body)

    @app.post("/ui/actions/configure", response_class=HTMLResponse)
    def run_configure(
        key: str = Form(...),
        value: str = Form(""),
        refresh_doctor: Optional[str] = Form(None),
        lang: str = Form(DEFAULT_LANGUAGE),
    ) -> HTMLResponse:
        active_lang = normalize_language(lang)
        if key not in ALLOWED_CONFIG_KEYS:
            raise HTTPException(status_code=400, detail=_t(active_lang, "unsupported_config_key"))
        if not value.strip():
            return HTMLResponse(
                _render_notice(_t(active_lang, "config_value_required"), error=True)
            )

        result = _run_cli(["configure", key, value.strip()])
        body = _render_command_result(_t(active_lang, "action_configure"), result, active_lang)
        if refresh_doctor is not None:
            body += _render_doctor_oob(active_lang)
        return HTMLResponse(body)

    @app.post("/ui/actions/browser-import", response_class=HTMLResponse)
    def run_browser_import(
        browser: str = Form("chrome"),
        refresh_doctor: Optional[str] = Form(None),
        lang: str = Form(DEFAULT_LANGUAGE),
    ) -> HTMLResponse:
        active_lang = normalize_language(lang)
        if browser not in ALLOWED_BROWSERS:
            raise HTTPException(status_code=400, detail=_t(active_lang, "unsupported_browser"))

        result = _run_cli(["configure", "--from-browser", browser])
        body = _render_command_result(_t(active_lang, "action_browser_import"), result, active_lang)
        if refresh_doctor is not None:
            body += _render_doctor_oob(active_lang)
        return HTMLResponse(body)

    @app.post("/ui/actions/setup", response_class=HTMLResponse)
    def run_setup(
        enable_exa: Optional[str] = Form(None),
        github_token: str = Form(""),
        reddit_proxy: str = Form(""),
        groq_key: str = Form(""),
        refresh_doctor: Optional[str] = Form(None),
        lang: str = Form(DEFAULT_LANGUAGE),
    ) -> HTMLResponse:
        active_lang = normalize_language(lang)
        notes, errors = _apply_guided_setup(
            enable_exa=enable_exa is not None,
            github_token=github_token.strip(),
            reddit_proxy=reddit_proxy.strip(),
            groq_key=groq_key.strip(),
            lang=active_lang,
        )

        body = _render_setup_feedback(notes, errors, active_lang)
        if refresh_doctor is not None:
            body += _render_doctor_oob(active_lang)
        return HTMLResponse(body)

    @app.post("/ui/actions/uninstall", response_class=HTMLResponse)
    def run_uninstall(
        dry_run: Optional[str] = Form(None),
        keep_config: Optional[str] = Form(None),
        refresh_doctor: Optional[str] = Form(None),
        lang: str = Form(DEFAULT_LANGUAGE),
    ) -> HTMLResponse:
        active_lang = normalize_language(lang)
        args = ["uninstall"]
        if dry_run is not None:
            args.append("--dry-run")
        if keep_config is not None:
            args.append("--keep-config")

        result = _run_cli(args)
        body = _render_command_result(_t(active_lang, "action_uninstall"), result, active_lang)
        if refresh_doctor is not None:
            body += _render_doctor_oob(active_lang)
        return HTMLResponse(body)

    return app


app = create_app()


def _run_cli(cli_args: List[str]) -> CommandResult:
    if not cli_args:
        raise HTTPException(status_code=400, detail="No command provided.")
    if cli_args[0] not in ALLOWED_CLI_COMMANDS:
        raise HTTPException(status_code=400, detail="Command is not allowed in UI.")

    env = os.environ.copy()
    python_bin_dir = str(Path(sys.executable).parent)
    env["PATH"] = python_bin_dir + os.pathsep + env.get("PATH", "")

    full_cmd = [sys.executable, "-m", "agent_reach.cli", *cli_args]

    try:
        proc = subprocess.run(
            full_cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=1800,
        )
        return CommandResult(
            command=" ".join(full_cmd),
            return_code=proc.returncode,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
        )
    except subprocess.TimeoutExpired as exc:
        out = _coerce_text(exc.stdout)
        err = _coerce_text(exc.stderr)
        err = (err + "\nCommand timed out after 1800 seconds.").strip()
        return CommandResult(
            command=" ".join(full_cmd),
            return_code=124,
            stdout=out.strip(),
            stderr=err,
        )


def _coerce_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return ""


def _apply_guided_setup(
    enable_exa: bool,
    github_token: str,
    reddit_proxy: str,
    groq_key: str,
    lang: str,
) -> Tuple[List[str], List[str]]:
    notes: List[str] = []
    errors: List[str] = []
    config = Config()

    if github_token:
        config.set("github_token", github_token)
        notes.append(_t(lang, "setup_saved_github"))

    if reddit_proxy:
        config.set("reddit_proxy", reddit_proxy)
        config.set("bilibili_proxy", reddit_proxy)
        notes.append(_t(lang, "setup_saved_proxy"))

    if groq_key:
        config.set("groq_api_key", groq_key)
        notes.append(_t(lang, "setup_saved_groq"))

    if enable_exa:
        exa_ok, exa_message = _ensure_exa_configured(lang)
        if exa_ok:
            notes.append(exa_message)
        else:
            errors.append(exa_message)

    if not notes and not errors:
        notes.append(_t(lang, "setup_no_change"))

    return notes, errors


def _ensure_exa_configured(lang: str) -> Tuple[bool, str]:
    mcporter = shutil.which("mcporter")
    if not mcporter:
        return False, _t(lang, "exa_missing_mcporter")

    try:
        existing = subprocess.run(
            [mcporter, "config", "list"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        haystack = (existing.stdout + "\n" + existing.stderr).lower()
        if "exa" in haystack:
            return True, _t(lang, "exa_already_configured")

        added = subprocess.run(
            [mcporter, "config", "add", "exa", "https://mcp.exa.ai/mcp"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        if added.returncode == 0:
            return True, _t(lang, "exa_configured")

        detail = (added.stderr or added.stdout or "Unknown error").strip()
        return False, _t(lang, "exa_setup_failed", detail=detail)
    except Exception as exc:
        return False, _t(lang, "exa_setup_failed", detail=str(exc))


def _redact_sensitive(text: str) -> str:
    masked = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = re.sub(pattern, replacement, masked)
    return masked


def _render_notice(message: str, error: bool = False) -> str:
    css_class = "notice-error" if error else "notice-ok"
    return f'<div class="notice {css_class}">{html.escape(message)}</div>'


def _render_setup_feedback(notes: List[str], errors: List[str], lang: str) -> str:
    output = [
        '<section class="result">',
        f"<h4>{html.escape(_t(lang, 'guided_setup_result'))}</h4>",
    ]

    if notes:
        output.append('<div class="notice notice-ok">')
        output.append("<ul>")
        for note in notes:
            output.append(f"<li>{html.escape(note)}</li>")
        output.append("</ul>")
        output.append("</div>")

    if errors:
        output.append('<div class="notice notice-error">')
        output.append("<ul>")
        for err in errors:
            output.append(f"<li>{html.escape(err)}</li>")
        output.append("</ul>")
        output.append("</div>")

    output.append("</section>")
    return "".join(output)


def _render_command_result(title: str, result: CommandResult, lang: str) -> str:
    state_class = "notice-ok" if result.return_code == 0 else "notice-error"
    command = html.escape(_redact_sensitive(result.command))
    stdout = html.escape(_redact_sensitive(result.stdout or _t(lang, "no_stdout")))
    stderr = html.escape(_redact_sensitive(result.stderr or ""))

    parts = [
        '<section class="result">',
        f"<h4>{html.escape(_t(lang, 'action_completed', action=title))}</h4>",
        f'<div class="notice {state_class}">',
        f"<strong>{html.escape(_t(lang, 'exit_code'))}:</strong> {result.return_code}<br>",
        f"<strong>{html.escape(_t(lang, 'command'))}:</strong> <code>{command}</code>",
        "</div>",
        f"<pre>{stdout}</pre>",
    ]
    if stderr:
        parts.append(f"<h5>{html.escape(_t(lang, 'stderr'))}</h5>")
        parts.append(f"<pre>{stderr}</pre>")

    parts.append("</section>")
    return "".join(parts)


def _render_doctor_oob(lang: str) -> str:
    doctor_html = _render_doctor_panel(AgentReach().doctor(), lang)
    return f'<div id="doctor-panel" hx-swap-oob="innerHTML">{doctor_html}</div>'


def _group_by_tier(results: Dict[str, dict]) -> Dict[int, List[Tuple[str, dict]]]:
    grouped: Dict[int, List[Tuple[str, dict]]] = {0: [], 1: [], 2: []}
    for key, data in results.items():
        tier = int(data.get("tier", 2))
        grouped.setdefault(tier, []).append((key, data))
    for tier in grouped:
        grouped[tier].sort(key=lambda item: item[1].get("name", item[0]).lower())
    return grouped


def _render_doctor_cards(items: List[Tuple[str, dict]], lang: str) -> str:
    cards: List[str] = []
    for key, data in items:
        status = data.get("status", "error")
        status_class = STATUS_CLASS.get(status, "status-error")
        status_label = _status_label(lang, str(status))
        name = html.escape(str(data.get("name", key)))
        message = html.escape(str(data.get("message", "")))
        backends = ", ".join(data.get("backends") or [])
        backend_html = html.escape(backends) if backends else html.escape(_t(lang, "not_available"))

        cards.append(
            """
      <article class="channel-card">
        <header>
          <h4>{name}</h4>
          <span class="status-pill {status_class}">{status_label}</span>
        </header>
        <p>{message}</p>
        <small>{backends_label}: {backend_html}</small>
      </article>
      """.format(
                name=name,
                status_class=status_class,
                status_label=html.escape(status_label),
                message=message,
                backend_html=backend_html,
                backends_label=html.escape(_t(lang, "backends")),
            )
        )
    return "".join(cards)


def _render_doctor_panel(results: Dict[str, dict], lang: str) -> str:
    grouped = _group_by_tier(results)
    ok_count = sum(1 for item in results.values() if item.get("status") == "ok")
    total = len(results)

    sections: List[str] = [
        '<section class="doctor-summary">',
        (
            f"<div><strong>{ok_count}/{total}</strong><span>"
            f"{html.escape(_t(lang, 'channels_ready'))}</span></div>"
        ),
        (
            f'<button class="ghost" hx-get="/ui/doctor?lang={html.escape(lang)}" '
            f'hx-target="#doctor-panel" hx-swap="innerHTML">'
            f"{html.escape(_t(lang, 'refresh'))}</button>"
        ),
        "</section>",
    ]

    for tier in (0, 1, 2):
        items = grouped.get(tier, [])
        if not items:
            continue
        sections.append(f"<h3>{html.escape(_tier_title(lang, tier))}</h3>")
        sections.append('<section class="channel-grid">')
        sections.append(_render_doctor_cards(items, lang))
        sections.append("</section>")

    return "".join(sections)


def _render_page(results: Dict[str, dict], lang: str) -> str:
    active_lang = normalize_language(lang)
    doctor_panel = _render_doctor_panel(results, active_lang)

    def txt(key: str) -> str:
        return html.escape(_t(active_lang, key))

    en_active = "active" if active_lang == "en" else ""
    tr_active = "active" if active_lang == "tr" else ""

    return f"""<!DOCTYPE html>
<html lang="{active_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{txt("page_title")}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style>
    :root {{
      --bg-1: #071722;
      --bg-2: #0b2434;
      --panel: #0d2d42cc;
      --line: #1f4d68;
      --txt: #f4fbff;
      --muted: #95b8cc;
      --accent: #ff7a18;
      --accent-2: #38d3b4;
      --ok: #3ddc97;
      --warn: #ffbe0b;
      --off: #9aa9b8;
      --error: #ff4d6d;
      --mono: "IBM Plex Mono", "Consolas", monospace;
      --display: "Chakra Petch", "Segoe UI", sans-serif;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      color: var(--txt);
      font-family: var(--display);
      background:
        radial-gradient(circle at 10% 15%, #1a5f7a 0%, transparent 35%),
        radial-gradient(circle at 85% 8%, #ff7a1844 0%, transparent 30%),
        linear-gradient(140deg, var(--bg-1), var(--bg-2));
      min-height: 100vh;
      overflow-x: hidden;
    }}

    body::before,
    body::after {{
      content: "";
      position: fixed;
      width: 26rem;
      height: 26rem;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.18;
      pointer-events: none;
      z-index: -1;
      animation: floatGlow 14s ease-in-out infinite;
    }}

    body::before {{
      background: #ff7a18;
      top: -9rem;
      left: -6rem;
    }}

    body::after {{
      background: #38d3b4;
      right: -8rem;
      bottom: -10rem;
      animation-delay: 4s;
    }}

    @keyframes floatGlow {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(24px); }}
    }}

    .container {{
      width: min(1200px, 94vw);
      margin: 0 auto;
      padding: 2rem 0 3rem;
      animation: rise 480ms ease-out;
    }}

    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(14px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero {{
      padding: 1.4rem 1.6rem;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: linear-gradient(120deg, #0f2f44f0, #134762d0);
      box-shadow: 0 20px 60px #00101850;
      margin-bottom: 1.3rem;
    }}

    .hero h1 {{
      margin: 0;
      font-size: clamp(1.5rem, 3vw, 2.4rem);
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}

    .hero p {{
      margin: 0.45rem 0 0;
      color: var(--muted);
      font-size: 0.98rem;
      max-width: 75ch;
    }}

    .lang-switch {{
      margin-top: 0.8rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--muted);
      font-size: 0.84rem;
    }}

    .lang-chip {{
      text-decoration: none;
      color: var(--txt);
      border: 1px solid #2e6e8f;
      border-radius: 999px;
      padding: 0.2rem 0.45rem;
      font-family: var(--mono);
      font-size: 0.75rem;
    }}

    .lang-chip.active {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    .layout {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 1rem;
    }}

    .stack {{
      display: grid;
      gap: 1rem;
      align-content: start;
    }}

    .panel {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--panel);
      backdrop-filter: blur(12px);
      padding: 1rem;
      box-shadow: 0 10px 30px #03121f3f;
    }}

    .panel h2 {{
      margin: 0 0 0.7rem;
      font-size: 1.05rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .doctor-summary {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.8rem;
      margin-bottom: 0.8rem;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.8rem;
      background: #0a2335;
    }}

    .doctor-summary strong {{
      display: block;
      font-size: 1.55rem;
      color: var(--accent);
      line-height: 1;
    }}

    .doctor-summary span {{
      color: var(--muted);
      font-size: 0.9rem;
    }}

    .channel-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.7rem;
      margin-bottom: 0.9rem;
    }}

    .channel-card {{
      border: 1px solid #1a4156;
      border-radius: 12px;
      padding: 0.75rem;
      background: #082134;
      animation: rise 420ms ease-out;
    }}

    .channel-card header {{
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 0.5rem;
      margin-bottom: 0.35rem;
    }}

    .channel-card h4 {{
      margin: 0;
      font-size: 0.97rem;
      letter-spacing: 0.02em;
    }}

    .channel-card p {{
      margin: 0.3rem 0 0.45rem;
      color: #d4e9f4;
      font-size: 0.88rem;
      line-height: 1.4;
    }}

    .channel-card small {{
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.75rem;
    }}

    .status-pill {{
      border-radius: 999px;
      font-size: 0.72rem;
      padding: 0.22rem 0.5rem;
      border: 1px solid currentColor;
      white-space: nowrap;
      font-family: var(--mono);
      font-weight: 500;
    }}

    .status-ok {{ color: var(--ok); }}
    .status-warn {{ color: var(--warn); }}
    .status-off {{ color: var(--off); }}
    .status-error {{ color: var(--error); }}

    h3 {{
      margin: 1rem 0 0.55rem;
      font-size: 0.9rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    form {{ display: grid; gap: 0.6rem; }}

    .field {{ display: grid; gap: 0.33rem; }}

    label {{
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    input,
    select {{
      width: 100%;
      border: 1px solid #23556f;
      border-radius: 10px;
      background: #041726;
      color: var(--txt);
      padding: 0.6rem 0.66rem;
      font: inherit;
      font-size: 0.92rem;
    }}

    input[type="checkbox"] {{
      width: auto;
      accent-color: var(--accent);
    }}

    .checkbox-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.8rem;
      align-items: center;
      color: var(--muted);
      font-size: 0.85rem;
    }}

    .btn-row {{
      display: flex;
      gap: 0.55rem;
      flex-wrap: wrap;
    }}

    button {{
      border: 0;
      border-radius: 10px;
      background: linear-gradient(120deg, var(--accent), #ff9d00);
      color: #111;
      font-family: var(--mono);
      font-weight: 600;
      letter-spacing: 0.04em;
      padding: 0.58rem 0.82rem;
      cursor: pointer;
      transition: transform 120ms ease, filter 120ms ease;
    }}

    button:hover {{
      transform: translateY(-1px);
      filter: brightness(1.05);
    }}

    button.ghost {{
      color: var(--txt);
      background: transparent;
      border: 1px solid #2e6e8f;
    }}

    .output,
    .result {{
      margin-top: 0.55rem;
      border: 1px solid #204d66;
      border-radius: 10px;
      background: #071b2b;
      padding: 0.65rem;
    }}

    .result h4,
    .result h5 {{ margin: 0 0 0.45rem; }}

    .notice {{
      border-radius: 9px;
      border: 1px solid #2f5d73;
      padding: 0.46rem 0.56rem;
      font-size: 0.86rem;
      margin-bottom: 0.55rem;
    }}

    .notice-ok {{
      border-color: #2f7a61;
      background: #0a2a23;
    }}

    .notice-error {{
      border-color: #7a3242;
      background: #2b1219;
    }}

    pre,
    code {{
      font-family: var(--mono);
      font-size: 0.78rem;
      line-height: 1.42;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    .danger {{
      border-color: #6f2b38;
      background: #2d1118;
    }}

    .legend {{
      color: var(--muted);
      font-size: 0.8rem;
      line-height: 1.45;
      margin-top: 0.5rem;
    }}

    @media (max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="container">
    <section class="hero">
      <h1>{txt("hero_title")}</h1>
      <p>
        {txt("hero_body")}
      </p>
      <div class="lang-switch">
        <span>{txt("language")}:</span>
        <a class="lang-chip {en_active}" href="/?lang=en">{txt("lang_en")}</a>
        <a class="lang-chip {tr_active}" href="/?lang=tr">{txt("lang_tr")}</a>
      </div>
    </section>

    <section class="layout">
      <section class="panel">
        <h2>{txt("doctor_dashboard")}</h2>
        <div id="doctor-panel">{doctor_panel}</div>
      </section>

      <section class="stack">
        <section class="panel">
          <h2>{txt("install")}</h2>
          <form hx-post="/ui/actions/install" hx-target="#install-output" hx-swap="innerHTML">
            <input type="hidden" name="lang" value="{active_lang}">
            <div class="field">
              <label for="install-env">{txt("environment")}</label>
              <select id="install-env" name="env">
                <option value="auto" selected>auto</option>
                <option value="local">local</option>
                <option value="server">server</option>
              </select>
            </div>
            <div class="field">
              <label for="install-proxy">{txt("proxy_optional")}</label>
              <input id="install-proxy" name="proxy" placeholder="http://user:pass@ip:port" />
            </div>
            <div class="checkbox-row">
              <label><input type="checkbox" name="safe"> {txt("safe_mode")}</label>
              <label><input type="checkbox" name="dry_run"> {txt("dry_run")}</label>
              <label><input type="checkbox" name="refresh_doctor" checked> {txt("refresh_doctor")}</label>
            </div>
            <div class="btn-row">
              <button type="submit">{txt("run_install")}</button>
            </div>
          </form>
          <div id="install-output" class="output">{txt("install_output_placeholder")}</div>
        </section>

        <section class="panel">
          <h2>{txt("configure")}</h2>
          <form hx-post="/ui/actions/configure" hx-target="#configure-output" hx-swap="innerHTML">
            <input type="hidden" name="lang" value="{active_lang}">
            <div class="field">
              <label for="configure-key">{txt("key")}</label>
              <select id="configure-key" name="key">
                <option value="proxy">proxy</option>
                <option value="github-token">github-token</option>
                <option value="groq-key">groq-key</option>
                <option value="twitter-cookies">twitter-cookies</option>
                <option value="youtube-cookies">youtube-cookies</option>
                <option value="xhs-cookies">xhs-cookies</option>
              </select>
            </div>
            <div class="field">
              <label for="configure-value">{txt("value")}</label>
              <input id="configure-value" name="value" type="password" placeholder="{txt("value_placeholder")}" />
            </div>
            <div class="checkbox-row">
              <label><input type="checkbox" name="refresh_doctor" checked> {txt("refresh_doctor")}</label>
            </div>
            <div class="btn-row">
              <button type="submit">{txt("save_config")}</button>
            </div>
          </form>

          <form hx-post="/ui/actions/browser-import" hx-target="#configure-output" hx-swap="innerHTML">
            <input type="hidden" name="lang" value="{active_lang}">
            <div class="field">
              <label for="browser">{txt("browser_import")}</label>
              <select id="browser" name="browser">
                <option value="chrome">chrome</option>
                <option value="edge">edge</option>
                <option value="firefox">firefox</option>
                <option value="brave">brave</option>
                <option value="opera">opera</option>
              </select>
            </div>
            <div class="checkbox-row">
              <label><input type="checkbox" name="refresh_doctor" checked> {txt("refresh_doctor")}</label>
            </div>
            <div class="btn-row">
              <button type="submit" class="ghost">{txt("import_cookies")}</button>
            </div>
          </form>
          <div id="configure-output" class="output">{txt("configure_output_placeholder")}</div>
        </section>

        <section class="panel">
          <h2>{txt("guided_setup")}</h2>
          <form hx-post="/ui/actions/setup" hx-target="#setup-output" hx-swap="innerHTML">
            <input type="hidden" name="lang" value="{active_lang}">
            <div class="checkbox-row">
              <label><input type="checkbox" name="enable_exa" checked> {txt("ensure_exa")}</label>
              <label><input type="checkbox" name="refresh_doctor" checked> {txt("refresh_doctor")}</label>
            </div>
            <div class="field">
              <label for="setup-github-token">{txt("github_token_optional")}</label>
              <input id="setup-github-token" name="github_token" type="password" placeholder="ghp_xxx" />
            </div>
            <div class="field">
              <label for="setup-reddit-proxy">{txt("reddit_proxy_optional")}</label>
              <input id="setup-reddit-proxy" name="reddit_proxy" placeholder="http://user:pass@ip:port" />
            </div>
            <div class="field">
              <label for="setup-groq-key">{txt("groq_key_optional")}</label>
              <input id="setup-groq-key" name="groq_key" type="password" placeholder="gsk_xxx" />
            </div>
            <div class="btn-row">
              <button type="submit">{txt("apply_setup")}</button>
            </div>
          </form>
          <div id="setup-output" class="output">{txt("setup_output_placeholder")}</div>
        </section>

        <section class="panel danger">
          <h2>{txt("uninstall")}</h2>
          <form hx-post="/ui/actions/uninstall" hx-target="#uninstall-output" hx-swap="innerHTML">
            <input type="hidden" name="lang" value="{active_lang}">
            <div class="checkbox-row">
              <label><input type="checkbox" name="dry_run" checked> {txt("dry_run_first")}</label>
              <label><input type="checkbox" name="keep_config"> {txt("keep_config")}</label>
              <label><input type="checkbox" name="refresh_doctor"> {txt("refresh_doctor")}</label>
            </div>
            <div class="btn-row">
              <button type="submit">{txt("run_uninstall")}</button>
            </div>
          </form>
          <p class="legend">
            {txt("uninstall_legend")}
          </p>
          <div id="uninstall-output" class="output">{txt("uninstall_output_placeholder")}</div>
        </section>
      </section>
    </section>
  </main>
</body>
</html>
"""


def cli_main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Reach local web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8787, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    cli_main()
