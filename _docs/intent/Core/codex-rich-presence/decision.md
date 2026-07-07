---
title: "Intent: Codex Rich Presence CLI"
status: active
draft_status: n/a
created_at: 2026-07-07
updated_at: 2026-07-07
references:
  - "_docs/plan/Core/codex-rich-presence/plan.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# Intent: Codex Rich Presence CLI

## Context

Codex作業中の状態をDiscordに表示したいが、プロンプト本文や対象ファイル名を外に出すと日常利用で情報量とプライバシーの釣り合いが崩れる。VSCode程度の粒度として、repo名、作業フェーズ、経過時間だけを基本表示にする。

## Decision

- Rich Presenceの基本表示は repo + phase + timer に限定する。
- Discordへ送るactivity nameは `Codex (Desktop)` とする。
- 表示言語は日本語をデフォルトにし、設定で英語へ切り替えられるようにする。
- GitHub remoteから `https://github.com/<owner>/<repo>` を確実に作れる場合だけ、`リポジトリを見る` ボタンを出す。
- Discord Rich Presence asset keyを設定した場合だけ、payloadにlarge image keyを含める。
- 実行環境でDiscord Desktopへ接続できなくても検証できるよう、payloadをJSONとして出す `render` コマンドを提供する。
- Codex内部hookには依存せず、state fileと `set-phase` コマンドで外部からフェーズ更新できる形にする。
- LinuxではCodex Desktop配下の `node_repl` process cwdをbest-effort project候補として検出する `monitor` コマンドを提供する。
- `monitor` はCodex Desktopの `~/.codex/state_5.sqlite` からproject recencyを読める場合、既定20分より古い候補を表示対象から外す。
- 複数のdistinct projectが検出された場合、単一projectを推定せず「N個のCodexプロジェクトで作業中」と集約表示し、repository buttonは出さない。
- `monitor` は検出状態の変化、Presence更新、clearをstderrへ簡潔に出力する。

## Alternatives

- PRボタンを常時表示する案: PRコンテキストを確実に取得できない場面が多く、初期版では過剰なので不採用。
- branch名やファイル名を出す案: 作業内容の漏れや誤表示のリスクが増えるため不採用。
- Discord公式Social SDKを直接使う案: Python CLIとしての軽量実装に合いにくいため、初期版ではローカルRPC互換の `pypresence` を使う。
- 複数project時に最新projectだけを表示する案: foreground threadを正確に特定できないため、誤表示を避ける目的で集約表示を採用する。

## Rationale

Rich Presenceは見た人に「今何をしているか」を伝えるための表示であり、開発中の詳細ログではない。repo名、フェーズ、timerに限定すると、VSCodeのPresenceに近い粒度を保ちつつ、Codex固有の状態も伝えられる。

## Consequences / Impact

- Discord Desktopが動いていない環境では `run` は利用できないが、`render` でpayload検証はできる。
- `client_id` はユーザー設定に置く必要がある。
- GitHub以外のremoteではボタンは表示されない。
- `monitor` の自動検出はLinux `/proc` とCodex Desktopの現在のprocess modelに依存する。
- Codex state DBが読めない場合、project recency filteringは行わず `/proc` 候補を使う。

## Quality Implications

- 表示対象を限定し、将来の変更でファイル名やプロンプト本文が混入しないようにする。
- GitHub URLの正規化は許可した形式だけを通し、不明なremoteからボタンを作らない。
- large image keyは設定値が空でない場合だけpayloadへ渡し、空の場合は従来通り画像なしにする。
- Discord接続なしで主要ロジックをテストできる状態を維持する。
- 複数project時はproject数だけを表示し、特定repoへのリンクを出さない。
- monitorログは常駐運用でjournalを汚しすぎないよう、状態変化時だけ出す。
- recency filteringではcwdとtimestampだけを読み、thread titleやcommand lineを表示に使わない。

## Intent-derived Invariants

- INV-001: Rich Presence payloadはrepo名、phase、timer、正規化済みGitHub URLボタン以外の作業詳細を含まない。
- INV-002: GitHubボタンは `git@github.com:owner/repo(.git)` または `https://github.com/owner/repo(.git)` から正規化できる場合だけ生成される。
- INV-003: 日本語表示がデフォルトであり、英語表示は明示設定時だけ使われる。
- INV-004: Discord接続なしでpayload生成を検証できるCLIとテストが存在する。
- INV-005: `monitor` は `node_repl` cwdからdistinct project rootを検出し、複数project時は単一repoとして表示しない。
- INV-006: `monitor` は認証ヘッダやcmdline全文を読まず、process cwd/exe/metadataだけを使ってproject候補を判定する。
- INV-007: large image keyは明示設定された場合だけDiscord payloadに含まれる。
- INV-008: `monitor` は検出状態が変わった時に、候補なし・単一project・複数project・clear/updateをstderrへ出力する。
- INV-009: Discord RPC payloadのactivity nameは `Codex (Desktop)` である。
- INV-010: `monitor` はCodex state DBからrecencyを読める候補について、`active_project_ttl_minutes` より古いprojectを表示対象から外す。

## Enforced in (optional)

- INV-001: `src/codex_discord_rpc/presence.py`, `tests/test_presence.py`
- INV-002: `src/codex_discord_rpc/git_info.py`, `tests/test_git_info.py`
- INV-003: `src/codex_discord_rpc/config.py`, `tests/test_presence.py`
- INV-004: `src/codex_discord_rpc/cli.py`, `tests/test_presence.py`
- INV-005: `src/codex_discord_rpc/project_detection.py`, `src/codex_discord_rpc/cli.py`, `tests/test_project_detection.py`, `tests/test_cli.py`
- INV-006: `src/codex_discord_rpc/project_detection.py`
- INV-007: `src/codex_discord_rpc/config.py`, `src/codex_discord_rpc/presence.py`, `tests/test_presence.py`
- INV-008: `src/codex_discord_rpc/cli.py`, `tests/test_cli.py`
- INV-009: `src/codex_discord_rpc/presence.py`, `tests/test_presence.py`
- INV-010: `src/codex_discord_rpc/project_detection.py`, `src/codex_discord_rpc/cli.py`, `tests/test_project_detection.py`

## Rollback / Follow-ups

- 問題があれば `enabled = false` にするか、`run` を止めればDiscord表示は消える。
- 将来、Codex側の安定hookが用意された場合は `set-phase` をhookから呼ぶ統合を追加できる。
- `node_repl` のprocess modelが変わった場合は `auto_detect_projects = false` に戻し、state/config projectを使う。
