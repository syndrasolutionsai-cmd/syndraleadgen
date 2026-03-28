from leadforge.icp.config import ICPConfig
from leadforge.scraping.aggregator import MergedProspect

# Weights per criterion (must sum to 100)
WEIGHTS = {
    "role": 35,
    "industry": 25,
    "company_size": 15,
    "geography": 10,
    "tech_signals": 15,
}


class ICPFilter:
    def __init__(self, config: ICPConfig):
        self.config = config

    def score(self, prospect: MergedProspect) -> float:
        """
        Return an ICP score 0-100. Returns 0 immediately if any exclude_signal found.
        """
        # Hard disqualifiers first
        all_text = self._prospect_text(prospect).lower()
        for exclude in self.config.exclude_signals:
            if exclude.lower() in all_text:
                return 0.0

        score = 0.0

        # Role match (30 pts)
        if prospect.role:
            for role in self.config.roles:
                if role.lower() in prospect.role.lower():
                    score += WEIGHTS["role"]
                    break

        # Industry match (25 pts)
        if prospect.industry:
            for industry in self.config.industries:
                if industry.lower() in prospect.industry.lower():
                    score += WEIGHTS["industry"]
                    break

        # Company size (15 pts)
        if prospect.company_size is not None:
            lo = self.config.company_size.get("min", 0)
            hi = self.config.company_size.get("max", 10_000)
            if lo <= prospect.company_size <= hi:
                score += WEIGHTS["company_size"]

        # Geography (10 pts) — skip check if no geo filter configured
        if not self.config.geography:
            score += WEIGHTS["geography"]
        elif prospect.geography:
            for geo in self.config.geography:
                if geo.lower() in prospect.geography.lower():
                    score += WEIGHTS["geography"]
                    break

        # Tech signals (20 pts) — partial credit if some signals match
        if self.config.tech_signals:
            matches = sum(
                1 for tech in self.config.tech_signals
                if any(tech.lower() in t.lower() for t in prospect.tech_stack)
            )
            ratio = matches / len(self.config.tech_signals)
            score += WEIGHTS["tech_signals"] * ratio
        else:
            score += WEIGHTS["tech_signals"]  # no filter = full points

        return round(score, 1)

    def filter(self, prospects: list[MergedProspect]) -> list[MergedProspect]:
        """Return only prospects meeting min_icp_score, with score attached."""
        result = []
        for p in prospects:
            s = self.score(p)
            if s >= self.config.min_icp_score:
                p.enriched_data["icp_score"] = s
                result.append(p)
        return result

    def _prospect_text(self, p: MergedProspect) -> str:
        """Flatten all prospect text for exclude-signal scanning."""
        parts = [p.role or "", p.industry or "", str(p.enriched_data)]
        return " ".join(parts)
