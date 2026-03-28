# tests/test_config.py
from leadforge.config import settings

def test_settings_loads():
    assert settings.database_url.startswith("postgresql")
    assert len(settings.secret_key) >= 32
