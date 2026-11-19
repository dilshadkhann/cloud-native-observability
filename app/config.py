"""Application settings, loaded from environment variables."""

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass

ENVIRONMENTS = frozenset({"development", "production"})
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "off"})


class ConfigError(ValueError):
    """An environment variable is malformed or inconsistent."""


@dataclass(frozen=True)
class Settings:
    environment: str
    enable_fault_endpoints: bool
    max_slow_seconds: float


def _parse_bool(name: str, raw: str) -> bool:
    value = raw.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true or false, got {raw!r}")


def _parse_positive_float(name: str, raw: str) -> float:
    try:
        value = float(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise ConfigError(f"{name} must be a finite number above 0, got {raw!r}")
    return value


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build Settings from ``env``, or from the process environment if omitted."""
    source = os.environ if env is None else env

    environment = source.get("APP_ENV", "development").strip().lower()
    if environment not in ENVIRONMENTS:
        raise ConfigError(
            f"APP_ENV must be one of {sorted(ENVIRONMENTS)}, got {environment!r}"
        )

    default_faults = "true" if environment == "development" else "false"
    enable_faults = _parse_bool(
        "ENABLE_FAULT_ENDPOINTS", source.get("ENABLE_FAULT_ENDPOINTS", default_faults)
    )
    if environment == "production" and enable_faults:
        raise ConfigError("ENABLE_FAULT_ENDPOINTS cannot be true in production")

    max_slow = _parse_positive_float(
        "MAX_SLOW_SECONDS", source.get("MAX_SLOW_SECONDS", "5")
    )

    return Settings(
        environment=environment,
        enable_fault_endpoints=enable_faults,
        max_slow_seconds=max_slow,
    )
