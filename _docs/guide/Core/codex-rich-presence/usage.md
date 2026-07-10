---
title: Codex Rich Presence operations guide
status: active
draft_status: n/a
created_at: 2026-07-10
updated_at: 2026-07-10
references:
  - "README.md"
  - "QUICKSTART.md"
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/qa/Core/codex-rich-presence/verification.md"
related_issues: []
related_prs: []
---

# Codex Rich Presence operations guide

## Install and start

The service uses this checkout and its `.venv`. Prepare them, edit the user config, then install:

```bash
uv sync --extra dev
uv run codex-discord-rpc init
uv run codex-discord-rpc doctor
./scripts/install-user-service.sh --dry-run
./scripts/install-user-service.sh --enable-now
```

`doctor` validates static config and runtime dependencies without requiring Discord Desktop to be running.

## Daily operation

```bash
systemctl --user status codex-discord-rpc.service
journalctl --user -u codex-discord-rpc.service -f
uv run codex-discord-rpc set-phase editing
```

Codex Desktopが起動中でactive projectがない場合は待機中Presenceを表示する。Discordがofflineの場合、serviceは
終了せずbounded backoffし、接続後に最新payloadまたはclearを送る。configured refresh intervalの同一updateは
`pypresence` pipe切断を検出するhealth probeであり、通常journalには記録しない。

## Recovery and rollback

Checkoutを移動した場合、または`.venv`を再作成した場合はinstallerを再実行する。

```bash
./scripts/install-user-service.sh --enable-now
```

Permanent configuration errorではunitがrestart loopを避けて停止する。configを修正してから再startする。

```bash
uv run codex-discord-rpc doctor
systemctl --user restart codex-discord-rpc.service
```

Rollbackはunitとconfigを削除せず、serviceだけを停止・無効化する。

```bash
./scripts/install-user-service.sh --disable-now
```

## Privacy boundary

Presenceにはrepo名、phase、timer、許可されたGitHub URLだけを使う。journalにはproject basename/countとRPC error
typeだけを記録し、absolute path、prompt、command、raw exception message、credentialを記録しない。
