import pytest

from app.config import ConfigError, Settings, load_settings


def test_defaults_to_development_with_fault_endpoints() -> None:
    assert load_settings({}) == Settings(
        environment="development",
        enable_fault_endpoints=True,
        max_slow_seconds=5.0,
    )


def test_production_disables_fault_endpoints_by_default() -> None:
    settings = load_settings({"APP_ENV": "production"})

    assert settings.environment == "production"
    assert settings.enable_fault_endpoints is False


def test_reads_explicit_values() -> None:
    settings = load_settings(
        {
            "APP_ENV": "development",
            "ENABLE_FAULT_ENDPOINTS": "false",
            "MAX_SLOW_SECONDS": "2.5",
        }
    )

    assert settings == Settings(
        environment="development",
        enable_fault_endpoints=False,
        max_slow_seconds=2.5,
    )


def test_production_rejects_fault_endpoints() -> None:
    with pytest.raises(ConfigError, match="cannot be true in production"):
        load_settings({"APP_ENV": "production", "ENABLE_FAULT_ENDPOINTS": "true"})


def test_rejects_unknown_environment() -> None:
    with pytest.raises(ConfigError, match="APP_ENV"):
        load_settings({"APP_ENV": "staging"})


@pytest.mark.parametrize("value", ["maybe", "2", ""])
def test_rejects_invalid_boolean(value: str) -> None:
    with pytest.raises(ConfigError, match="ENABLE_FAULT_ENDPOINTS"):
        load_settings({"ENABLE_FAULT_ENDPOINTS": value})


@pytest.mark.parametrize("value", ["abc", "0", "-1", "nan", "inf", ""])
def test_rejects_invalid_max_slow_seconds(value: str) -> None:
    with pytest.raises(ConfigError, match="MAX_SLOW_SECONDS"):
        load_settings({"MAX_SLOW_SECONDS": value})


def test_reads_process_environment_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ENABLE_FAULT_ENDPOINTS", raising=False)

    assert load_settings().environment == "production"
