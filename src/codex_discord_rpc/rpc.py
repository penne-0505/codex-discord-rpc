from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Protocol


class PresenceClient(Protocol):
    def connect(self) -> None: ...

    def update(self, **kwargs: object) -> object: ...

    def clear(self) -> object: ...

    def close(self) -> None: ...


PresenceFactory = Callable[[], PresenceClient]
ErrorClassifier = Callable[[BaseException], bool]
_NO_STATE = object()


@dataclass(frozen=True)
class BackoffPolicy:
    initial_delay: float = 1.0
    multiplier: float = 2.0
    maximum_delay: float = 30.0

    def __post_init__(self) -> None:
        if self.initial_delay <= 0:
            raise ValueError("initial_delay must be positive")
        if self.multiplier < 1:
            raise ValueError("multiplier must be at least 1")
        if self.maximum_delay < self.initial_delay:
            raise ValueError("maximum_delay must not be less than initial_delay")


@dataclass(frozen=True)
class CoordinatorEvent:
    kind: str
    error_type: str | None = None
    retry_seconds: float | None = None
    health_refresh: bool = False


class PermanentPresenceError(RuntimeError):
    def __init__(self, error_type: str) -> None:
        self.error_type = error_type
        super().__init__(f"permanent Discord RPC error: {error_type}")


def is_permanent_presence_error(error: BaseException) -> bool:
    return type(error).__name__ == "InvalidID" or getattr(error, "code", None) == 4000


class PresenceCoordinator:
    """Keep the latest desired Presence across transient Discord IPC churn."""

    def __init__(
        self,
        factory: PresenceFactory,
        *,
        backoff: BackoffPolicy = BackoffPolicy(),
        refresh_interval: float = 15.0,
        is_permanent_error: ErrorClassifier = is_permanent_presence_error,
    ) -> None:
        if refresh_interval <= 0:
            raise ValueError("refresh_interval must be positive")
        self._factory = factory
        self._backoff = backoff
        self._refresh_interval = refresh_interval
        self._is_permanent_error = is_permanent_error
        self._client: PresenceClient | None = None
        self._desired: dict[str, object] | None | object = _NO_STATE
        self._desired_signature: str | object = _NO_STATE
        self._sent_signature: str | object = _NO_STATE
        self._next_attempt_at = 0.0
        self._next_delay = backoff.initial_delay
        self._next_refresh_at = 0.0
        self._shutdown = False

    @property
    def connected(self) -> bool:
        return self._client is not None

    @property
    def next_attempt_at(self) -> float:
        return self._next_attempt_at

    @property
    def desired(self) -> dict[str, object] | None:
        if self._desired is _NO_STATE:
            return None
        return deepcopy(self._desired)

    def set_desired(self, activity: Mapping[str, object] | None) -> bool:
        desired = None if activity is None else deepcopy(dict(activity))
        signature = _signature(desired)
        if signature == self._desired_signature:
            return False
        self._desired = desired
        self._desired_signature = signature
        return True

    def next_action_at(self, fallback: float) -> float:
        if self._client is None:
            return min(fallback, self._next_attempt_at)
        if self._desired is not None and self._desired is not _NO_STATE:
            return min(fallback, self._next_refresh_at)
        return fallback

    def pump(self, now: float) -> tuple[CoordinatorEvent, ...]:
        if self._shutdown or self._desired is _NO_STATE:
            return ()

        events: list[CoordinatorEvent] = []
        if self._client is None:
            if now < self._next_attempt_at:
                return ()
            candidate = self._factory()
            try:
                candidate.connect()
            except Exception as error:
                self._safe_close(candidate)
                if self._is_permanent_error(error):
                    raise PermanentPresenceError(type(error).__name__) from error
                return (self._schedule_retry(now, error),)
            self._client = candidate
            self._sent_signature = _NO_STATE
            events.append(CoordinatorEvent("connected"))

        changed = self._sent_signature != self._desired_signature
        health_refresh = (
            not changed
            and self._desired is not None
            and self._desired is not _NO_STATE
            and now >= self._next_refresh_at
        )
        if not changed and not health_refresh:
            return tuple(events)

        assert self._client is not None
        try:
            if self._desired is None:
                self._client.clear()
                kind = "cleared"
            else:
                self._client.update(**self._desired)
                kind = "updated"
        except Exception as error:
            self._drop_client()
            if self._is_permanent_error(error):
                raise PermanentPresenceError(type(error).__name__) from error
            events.append(self._schedule_retry(now, error))
            return tuple(events)

        self._sent_signature = self._desired_signature
        self._next_attempt_at = now
        self._next_delay = self._backoff.initial_delay
        self._next_refresh_at = now + self._refresh_interval
        events.append(CoordinatorEvent(kind, health_refresh=health_refresh))
        return tuple(events)

    def shutdown(self) -> bool:
        if self._shutdown:
            return False
        self._shutdown = True
        cleared = False
        if self._client is not None:
            try:
                if self._sent_signature not in {_NO_STATE, _signature(None)}:
                    self._client.clear()
                    cleared = True
            except Exception:
                pass
            finally:
                self._drop_client()
        return cleared

    def _schedule_retry(self, now: float, error: BaseException) -> CoordinatorEvent:
        delay = self._next_delay
        self._next_attempt_at = now + delay
        self._next_delay = min(self._backoff.maximum_delay, delay * self._backoff.multiplier)
        return CoordinatorEvent(
            "retry",
            error_type=type(error).__name__,
            retry_seconds=delay,
        )

    def _drop_client(self) -> None:
        if self._client is not None:
            self._safe_close(self._client)
        self._client = None
        self._sent_signature = _NO_STATE

    @staticmethod
    def _safe_close(client: PresenceClient) -> None:
        try:
            client.close()
        except Exception:
            # pypresence.close() asserts when connect() failed before a writer
            # existed. Close its event loop directly so repeated offline retries
            # do not accumulate loop resources.
            loop = getattr(client, "loop", None)
            try:
                if loop is not None and not loop.is_closed():
                    loop.close()
            except Exception:
                pass


def _signature(activity: Mapping[str, object] | None) -> str:
    return json.dumps(
        activity,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
