from leadforge.config import settings, Settings


def test_settings_loads():
    assert settings.database_url.startswith("postgresql")
    assert len(settings.secret_key) >= 32


def test_settings_env_override(monkeypatch):
    """Settings correctly picks up environment variable overrides."""
    monkeypatch.setenv("SECRET_KEY", "a-custom-secret-key-for-testing-purposes-here")
    custom = Settings()
    assert custom.secret_key == "a-custom-secret-key-for-testing-purposes-here"


def test_api_keys_default_empty():
    """API keys default to empty string, not None — callers must check."""
    assert settings.apify_api_token == ""
    assert isinstance(settings.anthropic_api_key, str)
