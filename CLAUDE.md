# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tool for automated badminton court booking at Hangzhou Dianzi University (杭电). Authenticates via DingTalk (钉钉) OAuth captured through mitmproxy, then interacts with the HDU sports facility API (`https://sportmeta.hdu.edu.cn/book/client/`).

## Development Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `requests`, `mitmproxy`, `schedule`.

## Key Commands

```bash
python3 badminton.py              # Main interactive CLI (booking, settings, token refresh)
python3 auto_grab.py              # Scheduled booking daemon (daily 20:00)
python3 auto_grab.py --run-now    # One-off immediate booking attempt
mitmdump -s capture_proxy.py -p 8080  # Capture DingTalk auth headers/token
python3 update_token.py           # Check token validity and account status
python3 my_bookings.py            # Query current bookings
```

No automated test suite. Validate changes manually via `python3 badminton.py` (menu flow) and `python3 my_bookings.py` (API/token handling).

## Architecture

Flat single-directory structure with task-focused scripts sharing a common core:

- **`badminton.py`** — Interactive terminal menu entry point (includes first-run guidance)
- **`booking_core.py`** — Centralized HTTP API client; all booking/query requests go through here (`API_BASE` constant)
- **`config_manager.py`** — Reads/writes persistent user config at `~/.badminton_config.json`
- **`auto_grab.py`** — Scheduled automation using `schedule` library; books "day after tomorrow" slots
- **`capture_proxy.py`** — mitmproxy addon that intercepts DingTalk login, saves token and headers locally
- **`update_token.py`** — Token status checker; auto-syncs JWT openid to local config
- **`my_bookings.py`** — Standalone booking query tool
- **`invite_partner.py`** — Standalone partner invitation tool

**Request flow:** User input → `booking_core` API calls → HTTP POST to HDU API → JSON response → terminal output.

**Booking flow:** Create booking info → Create order → (Optional) Invite partner.

**Auth flow:** mitmproxy captures DingTalk login → extracts Bearer token to `token.txt` and headers to `headers.json` → config_manager syncs identity (openid, nickname, phone). Tokens expire every ~2 hours.

## Coding Conventions

- Python 3, 4-space indentation
- `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for module constants
- CLI text is in Chinese; preserve existing Chinese copy unless revising the full interaction flow
- Move shared API/config logic into `booking_core.py` or `config_manager.py` rather than duplicating
- Commits use Conventional Commit prefixes with concise Chinese summaries (e.g., `feat: 添加候补预约功能`)

## Security

Never commit `token.txt`, `headers.json`, phone numbers, or `openid` values. User-specific values belong in `~/.badminton_config.json`, not hardcoded in scripts.
