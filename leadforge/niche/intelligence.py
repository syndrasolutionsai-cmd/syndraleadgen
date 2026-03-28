from dataclasses import dataclass, field
from datetime import datetime

# Static niche knowledge base — enriched with research-backed scores.
# These are starting estimates; they update as campaign metrics come in.
NICHE_KNOWLEDGE: dict[str, dict] = {
    "B2B SaaS": {
        "prospect_density": 90,    # 0-100: how many contactable prospects exist
        "pain_signals": 85,        # 0-100: how loudly they advertise pain
        "ticket_size": 80,         # 0-100: proxy for deal value
        "outbound_saturation": 60, # 0-100: how saturated (lower = better for us)
        "notes": "High density, high ticket. SDR job postings everywhere = no outbound system. Slightly saturated but personalization cuts through.",
    },
    "Management Consulting": {
        "prospect_density": 60,
        "pain_signals": 70,
        "ticket_size": 95,
        "outbound_saturation": 30,
        "notes": "Very high ticket ($50K+ engagements). Low cold email saturation. Partners are relationship-driven — hyper-personalization essential.",
    },
    "Legal Tech": {
        "prospect_density": 50,
        "pain_signals": 65,
        "ticket_size": 85,
        "outbound_saturation": 25,
        "notes": "Smaller universe but low competition from outbound agencies. High deal value. Niche vocabulary critical.",
    },
    "Marketing Agencies": {
        "prospect_density": 85,
        "pain_signals": 80,
        "ticket_size": 55,
        "outbound_saturation": 90,
        "notes": "Very saturated. Agency owners receive dozens of cold emails daily. Only ultra-personalized outreach works.",
    },
    "Staffing & Recruiting": {
        "prospect_density": 75,
        "pain_signals": 85,
        "ticket_size": 70,
        "outbound_saturation": 55,
        "notes": "High pain: commission-based, always hungry for clients. Decent ticket. Moderate saturation.",
    },
    "Financial Advisory": {
        "prospect_density": 55,
        "pain_signals": 60,
        "ticket_size": 90,
        "outbound_saturation": 35,
        "notes": "Compliance-heavy — messaging must be conservative. Very high ACV. Low outbound saturation.",
    },
}

# Scoring weights
WEIGHTS = {
    "prospect_density": 0.20,
    "pain_signals": 0.25,
    "ticket_size": 0.35,
    "outbound_saturation_inv": 0.20,  # inverted: lower saturation = higher score
}


@dataclass
class NicheScore:
    niche: str
    total_score: float
    prospect_density: int
    pain_signals: int
    ticket_size: int
    outbound_saturation: int
    notes: str
    breakdown: dict = field(default_factory=dict)


class NicheScorer:
    def score_niche(self, niche: str) -> NicheScore:
        kb = NICHE_KNOWLEDGE.get(niche)
        if not kb:
            # Unknown niche — assign neutral scores
            kb = {
                "prospect_density": 50, "pain_signals": 50,
                "ticket_size": 50, "outbound_saturation": 50,
                "notes": "Unknown niche — limited data available.",
            }

        sat_inv = 100 - kb["outbound_saturation"]
        total = (
            kb["prospect_density"] * WEIGHTS["prospect_density"]
            + kb["pain_signals"] * WEIGHTS["pain_signals"]
            + kb["ticket_size"] * WEIGHTS["ticket_size"]
            + sat_inv * WEIGHTS["outbound_saturation_inv"]
        )
        return NicheScore(
            niche=niche,
            total_score=round(total, 1),
            prospect_density=kb["prospect_density"],
            pain_signals=kb["pain_signals"],
            ticket_size=kb["ticket_size"],
            outbound_saturation=kb["outbound_saturation"],
            notes=kb["notes"],
            breakdown={
                "density_contribution": kb["prospect_density"] * WEIGHTS["prospect_density"],
                "pain_contribution": kb["pain_signals"] * WEIGHTS["pain_signals"],
                "ticket_contribution": kb["ticket_size"] * WEIGHTS["ticket_size"],
                "saturation_contribution": sat_inv * WEIGHTS["outbound_saturation_inv"],
            },
        )

    def rank_niches(self, niches: list[str]) -> list[NicheScore]:
        scores = [self.score_niche(n) for n in niches]
        return sorted(scores, key=lambda s: s.total_score, reverse=True)

    def generate_report(self, scores: list[NicheScore]) -> str:
        lines = [
            f"# Niche Intelligence Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            f"## Recommended: {scores[0].niche} (Score: {scores[0].total_score}/100)",
            f"{scores[0].notes}",
            "",
            "## Full Ranking",
        ]
        for i, s in enumerate(scores, 1):
            lines.append(
                f"{i}. **{s.niche}** — {s.total_score}/100 "
                f"(Density: {s.prospect_density}, Pain: {s.pain_signals}, "
                f"Ticket: {s.ticket_size}, Saturation: {s.outbound_saturation})"
            )
        return "\n".join(lines)
