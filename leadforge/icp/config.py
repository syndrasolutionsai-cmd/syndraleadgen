# leadforge/icp/config.py
from dataclasses import dataclass, field
from typing import Any
import yaml


@dataclass
class ICPConfig:
    industries: list[str]
    roles: list[str]
    company_size: dict[str, int] = field(default_factory=lambda: {"min": 1, "max": 10_000})
    geography: list[str] = field(default_factory=list)
    tech_signals: list[str] = field(default_factory=list)
    exclude_signals: list[str] = field(default_factory=list)
    min_icp_score: float = 70.0

    def __post_init__(self):
        if not (0 <= self.min_icp_score <= 100):
            raise ValueError(f"min_icp_score must be 0-100, got {self.min_icp_score}")
        if not self.industries:
            raise ValueError("industries must not be empty")
        if not self.roles:
            raise ValueError("roles must not be empty")


def load_icp_config(yaml_str: str) -> ICPConfig:
    """Parse a YAML string into an ICPConfig, applying defaults."""
    data: dict[str, Any] = yaml.safe_load(yaml_str) or {}
    return ICPConfig(
        industries=data.get("industries", []),
        roles=data.get("roles", []),
        company_size=data.get("company_size", {"min": 1, "max": 10_000}),
        geography=data.get("geography", []),
        tech_signals=data.get("tech_signals", []),
        exclude_signals=data.get("exclude_signals", []),
        min_icp_score=float(data.get("min_icp_score", 70.0)),
    )
