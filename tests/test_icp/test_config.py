# tests/test_icp/test_config.py
import pytest
from leadforge.icp.config import ICPConfig, load_icp_config


VALID_ICP_YAML = """
industries:
  - SaaS B2B
  - Consulting
company_size:
  min: 10
  max: 500
roles:
  - CEO
  - Founder
geography:
  - US
  - UK
tech_signals:
  - HubSpot
exclude_signals:
  - hiring freeze
min_icp_score: 70
"""


def test_load_valid_icp():
    config = load_icp_config(VALID_ICP_YAML)
    assert config.min_icp_score == 70
    assert "CEO" in config.roles
    assert config.company_size["min"] == 10


def test_defaults_applied():
    minimal = "industries:\n  - SaaS\nroles:\n  - CEO\n"
    config = load_icp_config(minimal)
    assert config.min_icp_score == 70  # default
    assert config.geography == []  # default: no geo filter


def test_invalid_score_raises():
    with pytest.raises(ValueError):
        load_icp_config("industries:\n  - SaaS\nroles:\n  - CEO\nmin_icp_score: 150\n")
