---
title: "Intent: Codex Rich Presence CLI"
status: active
draft_status: n/a
created_at: 2026-07-07
updated_at: 2026-07-10
references:
  - "_docs/archives/plan/Core/codex-rich-presence/plan.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# Intent: Codex Rich Presence CLI

## Context

Codex作業中の状態をDiscordに表示したいが、プロンプト本文や対象ファイル名を外に出すと日常利用で情報量とプライバシーの釣り合いが崩れる。VSCode程度の粒度として、repo名、作業フェーズ、経過時間だけを基本表示にする。

日常利用ではforegroundで`monitor`を起動し続ける操作を要求せず、DiscordとCodex Desktopの起動順や再起動に
追従するuser serviceが必要である。常駐journalはterminalより永続性が高いため、absolute pathやraw errorを
出さない境界も強化する。

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
- project候補がなくてもCodex DesktopのElectron本体が起動中なら、「待機中」と表示する。
- `monitor` は検出状態の変化、Presence更新、clearをstderrへ簡潔に出力する。
- checkout直結のsystemd user serviceを正規の常駐経路とし、Codex Desktop起動中・active projectなしでも待機中表示を維持する。
- Discord未起動、pipe切断、timeoutはmonitor内部でbounded reconnectし、systemd restartを通常回復経路にしない。
- reconnect中はlatest desired payloadだけを保持し、接続後にpayloadまたはclearを即時replayする。
- `pypresence`はbackground pipe readerを持たないため、configured refresh intervalの同一updateを切断検出用health probeとして意図的に残す。
- SIGINT / SIGTERMはbest-effort clearとcloseを行い、Discord切断済みのclear失敗は正常終了を妨げない。
- journalにはproject basename/countとexception typeだけを出し、absolute path、raw exception message、secretを出さない。
- static doctorはconfig、client ID、dependency、checkout runtimeを確認するが、Discord起動中であることを要求しない。
- user unitは`NoNewPrivileges`とAF_UNIX限定を使うが、unprivileged filesystem namespaceを作る`PrivateTmp` / `ProtectSystem` / `ProtectHome`は使わない。他desktop processの`/proc/*/exe` / `cwd`が読めず、project検出と待機中判定を壊すためである。

## Alternatives

- PRボタンを常時表示する案: PRコンテキストを確実に取得できない場面が多く、初期版では過剰なので不採用。
- branch名やファイル名を出す案: 作業内容の漏れや誤表示のリスクが増えるため不採用。
- Discord公式Social SDKを直接使う案: Python CLIとしての軽量実装に合いにくいため、初期版ではローカルRPC互換の `pypresence` を使う。
- 複数project時に最新projectだけを表示する案: foreground threadを正確に特定できないため、誤表示を避ける目的で集約表示を採用する。
- systemd `Restart=on-failure`だけでDiscord再起動へ追従する案: timerがresetし、latest desired clearを保持できず、通常のDesktop起動順をprocess failureとして扱うため不採用。
- 同一payloadを完全に抑止する案: synchronous pypresenceではRPC requestがpipe切断検出を兼ねるため不採用。15秒既定のhealth refreshを残す。
- user-local packageへcopy installする案: development checkoutと実行versionがずれるため現段階では不採用。checkout安定後に再評価できる。

## Rationale

Rich Presenceは見た人に「今何をしているか」を伝えるための表示であり、開発中の詳細ログではない。repo名、フェーズ、timerに限定すると、VSCodeのPresenceに近い粒度を保ちつつ、Codex固有の状態も伝えられる。

## Consequences / Impact

- Discord Desktopが動いていない環境では `run` は利用できないが、`render` でpayload検証はできる。
- `client_id` はユーザー設定に置く必要がある。
- GitHub以外のremoteではボタンは表示されない。
- `monitor` の自動検出はLinux `/proc` とCodex Desktopの現在のprocess modelに依存する。
- Codex state DBが読めない場合、project recency filteringは行わず `/proc` 候補を使う。
- 待機中判定はCodex Desktop Electron本体のprocessだけを使い、残存 `node_repl` processだけでは待機中にしない。
- service unitはcheckoutと`.venv`の絶対pathへ依存し、移動・再作成後はinstaller再実行が必要になる。
- `/proc`検出を維持するため、systemd filesystem namespaceによる分離は採用できない。serviceのfilesystem accessはcurrent userと同等になる。
- permanent config / client ID errorではserviceを停止状態にし、transient Discord absenceではmonitor processを維持する。

## Quality Implications

- 表示対象を限定し、将来の変更でファイル名やプロンプト本文が混入しないようにする。
- GitHub URLの正規化は許可した形式だけを通し、不明なremoteからボタンを作らない。
- large image keyは設定値が空でない場合だけpayloadへ渡し、空の場合は従来通り画像なしにする。
- Discord接続なしで主要ロジックをテストできる状態を維持する。
- 複数project時はproject数だけを表示し、特定repoへのリンクを出さない。
- monitorログは常駐運用でjournalを汚しすぎないよう、状態変化時だけ出す。
- recency filteringではcwdとtimestampだけを読み、thread titleやcommand lineを表示に使わない。
- 待機中表示ではrepository buttonを出さない。
- reconnect coordinatorはwall clockやsleepに埋め込まず、monotonic timeとfake transportで検証可能にする。
- desired stateがclearへ変わった後に古いpayloadをreplayしてはならない。
- shutdown clearは時間制限付きかつidempotentで、接続喪失をtracebackやfailure exitにしない。
- journal向けstatus logはabsolute project pathとraw exception textを含めない。
- service preflightはDiscord offlineをfailureにせず、permanent configuration failureだけを拒否する。
- unit hardening変更時は実user service内からCodex Desktop processとnode_repl候補が見えることを再検証する。

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
- INV-011: `monitor` はCodex Desktop Electron本体が起動中かつactive projectがない場合に待機中payloadを出し、`node_repl` 単独では待機中にしない。
- INV-012: transient Discord IPC failureはmonitor processを終了させずbounded retryし、reconnect後にlatest desired stateだけをreplayしなければならない。
- INV-013: desired stateがclearへ変わった後は、reconnectしても古いPresence payloadを再送してはならない。
- INV-014: SIGINT / SIGTERM shutdownはbest-effort clearとcloseを一度だけ実行し、IPC failureでも正常終了しなければならない。
- INV-015: 常駐serviceでもCodex Desktop起動中・active projectなしは待機中payloadを維持しなければならない。
- INV-016: configured refresh intervalの同一updateはpypresence pipe health probeとしてのみ許可し、それより高頻度に送ってはならない。
- INV-017: monitor / service logはabsolute project path、raw exception message、prompt、command、secretを含んではならない。
- INV-018: static doctorとinstallerはDiscordの起動を要求せず、checkout runtimeとpermanent configurationだけをgateしなければならない。

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
- INV-011: `src/codex_discord_rpc/project_detection.py`, `src/codex_discord_rpc/presence.py`, `src/codex_discord_rpc/cli.py`, `tests/test_project_detection.py`, `tests/test_presence.py`, `tests/test_cli.py`
- INV-012〜016: `src/codex_discord_rpc/rpc.py`, `src/codex_discord_rpc/cli.py`, `tests/test_rpc.py`, `tests/test_cli.py`
- INV-017: `src/codex_discord_rpc/cli.py`, `tests/test_cli.py`, live journal review
- INV-018: `src/codex_discord_rpc/cli.py`, `scripts/install-user-service.sh`, service static/integration checks

## Rollback / Follow-ups

- 問題があれば `enabled = false` にするか、`run` を止めればDiscord表示は消える。
- 将来、Codex側の安定hookが用意された場合は `set-phase` をhookから呼ぶ統合を追加できる。
- `node_repl` のprocess modelが変わった場合は `auto_detect_projects = false` に戻し、state/config projectを使う。
- serviceは`scripts/install-user-service.sh --disable-now`で停止・無効化し、configとunitを保持したまま調査できる。
