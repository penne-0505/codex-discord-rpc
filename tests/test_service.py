from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-user-service.sh"
UNIT_TEMPLATE = ROOT / "packaging" / "systemd" / "codex-discord-rpc.service.in"


def _fake_systemctl(tmp_path: Path) -> tuple[Path, Path]:
    log_path = tmp_path / "systemctl.log"
    script_path = tmp_path / "systemctl"
    script_path.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$*" >> "$SYSTEMCTL_LOG"\n',
        encoding="utf-8",
    )
    script_path.chmod(0o755)
    return script_path, log_path


def test_ac013_installer_enables_and_restarts_checkout_service(tmp_path: Path) -> None:
    fake_systemctl, log_path = _fake_systemctl(tmp_path)
    config_home = tmp_path / "config"
    config_dir = config_home / "codex-discord-rpc"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text('client_id = "123"\n', encoding="utf-8")
    environment = os.environ | {
        "XDG_CONFIG_HOME": str(config_home),
        "SYSTEMCTL_BIN": str(fake_systemctl),
        "SYSTEMCTL_LOG": str(log_path),
    }

    result = subprocess.run(
        [str(INSTALLER), "--enable-now"],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    calls = log_path.read_text(encoding="utf-8").splitlines()
    assert calls == [
        "--user daemon-reload",
        "--user enable codex-discord-rpc.service",
        "--user restart codex-discord-rpc.service",
    ]
    unit = (config_home / "systemd" / "user" / "codex-discord-rpc.service").read_text()
    assert f"WorkingDirectory={ROOT}" in unit
    assert f"ExecStart={ROOT}/.venv/bin/codex-discord-rpc" in unit


def test_ac013_disable_retains_files_and_only_disables_service(tmp_path: Path) -> None:
    fake_systemctl, log_path = _fake_systemctl(tmp_path)
    environment = os.environ | {
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "SYSTEMCTL_BIN": str(fake_systemctl),
        "SYSTEMCTL_LOG": str(log_path),
    }

    result = subprocess.run(
        [str(INSTALLER), "--disable-now"],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert log_path.read_text(encoding="utf-8").strip() == (
        "--user disable --now codex-discord-rpc.service"
    )
    assert "config and unit were retained" in result.stdout


def test_inv015_unit_hardening_preserves_cross_process_proc_detection() -> None:
    unit = UNIT_TEMPLATE.read_text(encoding="utf-8")

    assert "NoNewPrivileges=true" in unit
    assert "RestrictAddressFamilies=AF_UNIX" in unit
    assert "PrivateTmp=" not in unit
    assert "ProtectSystem=" not in unit
    assert "ProtectHome=" not in unit


def test_ac015_unit_prevents_permanent_failure_restart_loop() -> None:
    unit = UNIT_TEMPLATE.read_text(encoding="utf-8")

    assert "Restart=on-failure" in unit
    assert "RestartPreventExitStatus=2 4" in unit
