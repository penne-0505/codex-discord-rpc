from __future__ import annotations

import pytest

from codex_discord_rpc.rpc import (
    BackoffPolicy,
    PermanentPresenceError,
    PresenceCoordinator,
)


class FakePresence:
    def __init__(
        self,
        *,
        connect_error: BaseException | None = None,
        update_error: BaseException | None = None,
        clear_error: BaseException | None = None,
    ) -> None:
        self.connect_error = connect_error
        self.update_error = update_error
        self.clear_error = clear_error
        self.connect_calls = 0
        self.updates: list[dict[str, object]] = []
        self.clear_calls = 0
        self.close_calls = 0

    def connect(self) -> None:
        self.connect_calls += 1
        if self.connect_error is not None:
            raise self.connect_error

    def update(self, **kwargs: object) -> None:
        if self.update_error is not None:
            error, self.update_error = self.update_error, None
            raise error
        self.updates.append(kwargs)

    def clear(self) -> None:
        self.clear_calls += 1
        if self.clear_error is not None:
            raise self.clear_error

    def close(self) -> None:
        self.close_calls += 1


class InvalidID(Exception):
    pass


class FakeLoop:
    def __init__(self) -> None:
        self.closed = False

    def is_closed(self) -> bool:
        return self.closed

    def close(self) -> None:
        self.closed = True


class UnconnectedPresence(FakePresence):
    def __init__(self) -> None:
        super().__init__(connect_error=FileNotFoundError())
        self.loop = FakeLoop()

    def close(self) -> None:
        raise AssertionError("writer is unavailable")


def factory_from(*clients: FakePresence):
    remaining = list(clients)

    def factory() -> FakePresence:
        return remaining.pop(0)

    return factory


def test_inv012_transient_connect_retries_and_replays_latest_desired() -> None:
    unavailable = FakePresence(connect_error=FileNotFoundError())
    recovered = FakePresence()
    coordinator = PresenceCoordinator(factory_from(unavailable, recovered))
    coordinator.set_desired({"details": "old"})

    events = coordinator.pump(0.0)
    coordinator.set_desired({"details": "latest"})

    assert events[-1].kind == "retry"
    assert events[-1].retry_seconds == 1.0
    assert coordinator.pump(0.5) == ()
    recovered_events = coordinator.pump(1.0)
    assert [event.kind for event in recovered_events] == ["connected", "updated"]
    assert recovered.updates == [{"details": "latest"}]


def test_inv013_clear_desired_wins_while_disconnected() -> None:
    unavailable = FakePresence(connect_error=FileNotFoundError())
    recovered = FakePresence()
    coordinator = PresenceCoordinator(factory_from(unavailable, recovered))
    coordinator.set_desired({"details": "stale"})
    coordinator.pump(0.0)

    coordinator.set_desired(None)
    events = coordinator.pump(1.0)

    assert [event.kind for event in events] == ["connected", "cleared"]
    assert recovered.updates == []
    assert recovered.clear_calls == 1


def test_inv012_update_failure_reconnects_with_latest_payload() -> None:
    disconnected = FakePresence(update_error=BrokenPipeError())
    recovered = FakePresence()
    coordinator = PresenceCoordinator(factory_from(disconnected, recovered))
    coordinator.set_desired({"details": "first"})

    events = coordinator.pump(0.0)
    coordinator.set_desired({"details": "second"})
    recovered_events = coordinator.pump(1.0)

    assert [event.kind for event in events] == ["connected", "retry"]
    assert disconnected.close_calls == 1
    assert [event.kind for event in recovered_events] == ["connected", "updated"]
    assert recovered.updates == [{"details": "second"}]


def test_inv016_same_payload_is_only_refreshed_at_configured_interval() -> None:
    client = FakePresence()
    coordinator = PresenceCoordinator(factory_from(client), refresh_interval=15.0)
    coordinator.set_desired({"details": "stable"})

    initial = coordinator.pump(0.0)
    before_due = coordinator.pump(14.9)
    refresh = coordinator.pump(15.0)

    assert [event.kind for event in initial] == ["connected", "updated"]
    assert before_due == ()
    assert len(client.updates) == 2
    assert refresh[-1].kind == "updated"
    assert refresh[-1].health_refresh is True


def test_inv014_shutdown_is_idempotent_and_tolerates_clear_failure() -> None:
    client = FakePresence(clear_error=BrokenPipeError())
    coordinator = PresenceCoordinator(factory_from(client))
    coordinator.set_desired({"details": "active"})
    coordinator.pump(0.0)

    assert coordinator.shutdown() is False
    assert coordinator.shutdown() is False
    assert client.clear_calls == 1
    assert client.close_calls == 1


def test_ac015_invalid_client_id_is_permanent() -> None:
    client = FakePresence(connect_error=InvalidID())
    coordinator = PresenceCoordinator(factory_from(client))
    coordinator.set_desired({"details": "active"})

    with pytest.raises(PermanentPresenceError, match="InvalidID"):
        coordinator.pump(0.0)


def test_inv012_backoff_is_bounded() -> None:
    clients = [FakePresence(connect_error=FileNotFoundError()) for _ in range(4)]
    coordinator = PresenceCoordinator(
        factory_from(*clients),
        backoff=BackoffPolicy(initial_delay=1.0, maximum_delay=4.0),
    )
    coordinator.set_desired({"details": "active"})

    delays = [
        coordinator.pump(0.0)[0].retry_seconds,
        coordinator.pump(1.0)[0].retry_seconds,
        coordinator.pump(3.0)[0].retry_seconds,
        coordinator.pump(7.0)[0].retry_seconds,
    ]

    assert delays == [1.0, 2.0, 4.0, 4.0]


def test_inv012_failed_connect_closes_pypresence_loop_resource() -> None:
    client = UnconnectedPresence()
    coordinator = PresenceCoordinator(factory_from(client))
    coordinator.set_desired({"details": "active"})

    coordinator.pump(0.0)

    assert client.loop.closed is True
