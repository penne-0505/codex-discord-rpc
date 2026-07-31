# Quickstart

## 1. 利用開始

```bash
uv sync --extra dev
uv run codex-discord-rpc init
```

`~/.config/codex-discord-rpc/config.toml` の `client_id` にDiscordアプリケーションのclient IDを設定します。

## 2. 表示確認

Discordに接続せず、Rich Presence payloadだけ確認します。

```bash
uv run codex-discord-rpc render --repo .
```

Discord Desktopへ反映する場合:

```bash
uv run codex-discord-rpc run --repo .
```

Codex Desktopのprojectを自動検出して反映する場合:

```bash
uv run codex-discord-rpc monitor
```

常駐serviceとして導入する場合:

```bash
uv run codex-discord-rpc doctor
./scripts/install-user-service.sh --dry-run
./scripts/install-user-service.sh --enable-now
systemctl --user status codex-discord-rpc.service
```

Discord Desktopが後から起動した場合や再起動した場合も、monitorが内部で再接続します。checkoutを移動した場合や
`.venv`を作り直した場合はinstallerを再実行してください。停止・rollbackは次を使います。

```bash
./scripts/install-user-service.sh --disable-now
```

フェーズ更新:

```bash
uv run codex-discord-rpc set-phase editing
uv run codex-discord-rpc set-phase running_tests
```

project pathを明示する場合:

```bash
uv run codex-discord-rpc set-project /path/to/project
```

## 3. 開発時に読むファイル

- [AGENTS.md](AGENTS.md)
- [TODO.md](TODO.md)
- [_docs/documentation_guide.md](_docs/documentation_guide.md)
- [_docs/intent/Core/codex-rich-presence/decision.md](_docs/intent/Core/codex-rich-presence/decision.md)
- [_docs/qa/Core/codex-rich-presence/test-plan.md](_docs/qa/Core/codex-rich-presence/test-plan.md)

## 4. 検証コマンド

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
./scripts/check-docs.sh
```

## 5. Docs workflow maintenance

### Agent lifecycle hooks

Codexは[`.codex/hooks.json`](.codex/hooks.json)、Claude Codeは[`.claude/settings.json`](.claude/settings.json)から共通の[`scripts/agent-workflow-hook.ts`](scripts/agent-workflow-hook.ts)を呼びます。Stop hookはgit subprocessの環境を安全に整えるため`--allow-env`を含む権限契約で実行します。hookはworkflow contextと安全確認を補助しますが、Riskやscopeを自動決定せず、docsの自動更新やQA evidenceの代替も行いません。初回利用時は各agentのhook設定を確認してください。

久しぶりの再開、handoff探索、docsのstale確認にはread-onlyの`docs-inventory` skillを使います。整理を実行する場合は棚卸し結果を確認してから`docs-cleanup`へ進みます。

### Template の継続更新

導入後のprojectへ新しいtemplate releaseを統合する場合は、moving `main`ではなく推奨tagを更新単位にします。

1. `docs-template.lock.json`から前回取り込んだtagとfull SHA (`B`)を確認する。
2. 取り込む推奨tag (`U`)をfull SHAへ解決する。
3. [`docs-template-migration`](.agents/skills/docs-template-migration/SKILL.md) skillで`B -> U`とproject customizationのthree-way inventoryを作る。
4. compatibility checksの成功後にlockを最後のmigration writeとして`U`へ更新する。
5. strict schema migrationの状態はlockではなくmigration verificationへ記録する。

`v1.0.0` より前に導入されたprojectはlockとlocal migration skillを持たない場合があります。repository history、導入記録、upstreamと一致するblobから最後に採用したcommit `B`を復元し、owner確認後に進めます。`v1.0.0`を中継する必要はなく、`v1.0.0`以降の任意の推奨 tag へ直接移行できます。`B`を一意に決められない場合は書き込み前に停止します。

`DD_SCOPE_BASE` は導入先 repository 内でvalidator対象を絞る値です。upstream template revisionを示す`docs-template.lock.json`とは用途が異なります。詳細は[template revision provenance](_docs/standards/documentation_operations.md#template-revision-provenance)を参照してください。
