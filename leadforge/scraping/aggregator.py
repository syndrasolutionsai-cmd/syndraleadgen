from dataclasses import dataclass, field
from typing import Any
from leadforge.scraping.base import ProspectRaw, ScraperSource, Signal


@dataclass
class MergedProspect:
    """A prospect confirmed by multiple scraping sources."""
    first_name: str
    last_name: str
    company_name: str
    confirmed_sources: list[ScraperSource]
    role: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    company_size: int | None = None
    industry: str | None = None
    geography: str | None = None
    tech_stack: list[str] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    enriched_data: dict[str, Any] = field(default_factory=dict)

    @property
    def is_confirmed(self) -> bool:
        return len(self.confirmed_sources) >= 2

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


def merge_prospect_data(prospects: list[ProspectRaw]) -> MergedProspect:
    """
    Merge multiple ProspectRaw records for the same person into one MergedProspect.
    Takes the first non-None value for scalar fields, merges lists, deduplicates signals.
    """
    if not prospects:
        raise ValueError("Cannot merge empty prospect list")

    base = prospects[0]
    merged = MergedProspect(
        first_name=base.first_name,
        last_name=base.last_name,
        company_name=base.company_name,
        confirmed_sources=[base.source],
    )

    for p in prospects[1:]:
        if p.source not in merged.confirmed_sources:
            merged.confirmed_sources.append(p.source)

    for p in prospects:
        if not merged.role and p.role:
            merged.role = p.role
        if not merged.email and p.email:
            merged.email = p.email
        if not merged.linkedin_url and p.linkedin_url:
            merged.linkedin_url = p.linkedin_url
        if not merged.company_size and p.company_size:
            merged.company_size = p.company_size
        if not merged.industry and p.industry:
            merged.industry = p.industry
        if not merged.geography and p.geography:
            merged.geography = p.geography
        # Merge tech stack (dedup)
        for tech in p.tech_stack:
            if tech not in merged.tech_stack:
                merged.tech_stack.append(tech)
        # Merge signals (dedup by type+source)
        existing_keys = {(s.signal_type, s.source) for s in merged.signals}
        for sig in p.signals:
            if (sig.signal_type, sig.source) not in existing_keys:
                merged.signals.append(sig)
                existing_keys.add((sig.signal_type, sig.source))
        # Merge enriched_data
        merged.enriched_data.update(p.enriched_data)

    return merged


def _normalize_name(name: str) -> str:
    return name.lower().strip().replace(".", "").replace("-", " ")


def _prospect_key(p: ProspectRaw) -> str:
    first = _normalize_name(p.first_name)
    last = _normalize_name(p.last_name)
    company = _normalize_name(p.company_name)
    return f"{first}|{last}|{company}"


class Aggregator:
    def __init__(self, min_sources: int = 2):
        self.min_sources = min_sources

    def aggregate(self, all_raw: list[ProspectRaw]) -> list[MergedProspect]:
        """
        Group raw prospects by identity key, merge each group, return only confirmed.
        """
        groups: dict[str, list[ProspectRaw]] = {}
        for p in all_raw:
            key = _prospect_key(p)
            groups.setdefault(key, []).append(p)

        merged_all = [merge_prospect_data(group) for group in groups.values()]
        return self.filter_confirmed(merged_all)

    def filter_confirmed(self, prospects: list[MergedProspect]) -> list[MergedProspect]:
        return [p for p in prospects if len(p.confirmed_sources) >= self.min_sources]
