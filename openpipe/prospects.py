"""Curated prospect pool — simulates directory / signal-based discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProspectSeed:
    full_name: str
    email: str
    title: str
    company: str
    industry: str
    city: str
    company_size: str
    trigger: str
    niche_tags: tuple[str, ...]


# Demo pool spanning OpenPipe's core verticals. Discovery filters this list.
PROSPECT_POOL: list[ProspectSeed] = [
    ProspectSeed(
        "Tendai Chirwa",
        "tendai@brightpathlogistics.co.zw",
        "Managing Director",
        "BrightPath Logistics",
        "Logistics",
        "Harare",
        "45 employees",
        "Just added 8 delivery vans after a retail contract win",
        ("fleet", "insurance", "sme", "logistics"),
    ),
    ProspectSeed(
        "Rudo Ncube",
        "rudo@avenuemedical.co.zw",
        "Practice Manager",
        "Avenue Medical Group",
        "Healthcare",
        "Harare",
        "28 employees",
        "Opened a second consulting room in Avondale",
        ("clinic", "insurance", "professional", "healthcare"),
    ),
    ProspectSeed(
        "Farai Dube",
        "farai@steelcityfab.co.zw",
        "Operations Director",
        "Steel City Fabrication",
        "Manufacturing",
        "Bulawayo",
        "70 employees",
        "Won a municipal tender — headcount up 15% this quarter",
        ("manufacturing", "insurance", "b2b", "tender"),
    ),
    ProspectSeed(
        "Aisha Patel",
        "aisha@patelretail.co.zw",
        "Owner",
        "Patel Retail Group",
        "Retail",
        "Harare",
        "120 employees",
        "Opening three new grocery outlets before year-end",
        ("retail", "insurance", "expansion", "sme"),
    ),
    ProspectSeed(
        "Sean Moyo",
        "sean@cloudnest.africa",
        "Founder & CEO",
        "CloudNest Africa",
        "SaaS",
        "Harare",
        "22 employees",
        "Closed a seed round and hiring engineers aggressively",
        ("saas", "advisor", "funding", "startup"),
    ),
    ProspectSeed(
        "Chiedza Gumbo",
        "chiedza@gumbolaw.co.zw",
        "Managing Partner",
        "Gumbo & Partners",
        "Legal",
        "Harare",
        "18 employees",
        "Promoted to managing partner; firm expanding corporate desk",
        ("legal", "advisor", "professional", "wealth"),
    ),
    ProspectSeed(
        "Tinashe Banda",
        "tinashe@bandafarms.co.zw",
        "Director",
        "Banda Agri Holdings",
        "Agriculture",
        "Mutare",
        "55 employees",
        "Export contract signed — new cold-storage build underway",
        ("agri", "insurance", "export", "sme"),
    ),
    ProspectSeed(
        "Nyasha Sibanda",
        "nyasha@orbitagency.co.zw",
        "Head of Growth",
        "Orbit Agency",
        "Marketing",
        "Harare",
        "35 employees",
        "Client roster doubled; looking for better ops systems",
        ("agency", "b2b", "growth", "marketing"),
    ),
    ProspectSeed(
        "Blessing Mhlanga",
        "blessing@metrobuild.co.zw",
        "Commercial Manager",
        "MetroBuild Contractors",
        "Construction",
        "Harare",
        "90 employees",
        "Three active commercial sites — liability questions rising",
        ("construction", "insurance", "commercial", "b2b"),
    ),
    ProspectSeed(
        "Kudzai Williams",
        "kudzai@finledge.co.zw",
        "CFO",
        "FinLedge Holdings",
        "Fintech",
        "Harare",
        "40 employees",
        "Preparing Series A; personal and corporate planning in flux",
        ("fintech", "advisor", "funding", "executive"),
    ),
    ProspectSeed(
        "Tatenda Chiriseri",
        "tatenda@northgateware.co.zw",
        "Warehouse Manager",
        "Northgate Warehousing",
        "Logistics",
        "Gweru",
        "60 employees",
        "Lease renewal next quarter on a larger facility",
        ("warehouse", "commercial_re", "logistics", "lease"),
    ),
    ProspectSeed(
        "Lindiwe Moyo",
        "lindiwe@sunrisehr.co.zw",
        "CHRO",
        "Sunrise Manufacturing",
        "Manufacturing",
        "Bulawayo",
        "200 employees",
        "Posted 12 open roles after a plant expansion",
        ("hiring", "recruiting", "manufacturing", "hr"),
    ),
    ProspectSeed(
        "James Okello",
        "james@okellotech.com",
        "IT Manager",
        "Okello Distribution",
        "Wholesale",
        "Harare",
        "85 employees",
        "Legacy servers failing — evaluating managed IT",
        ("it", "it_msp", "wholesale", "security"),
    ),
    ProspectSeed(
        "Grace Mutasa",
        "grace@mutasabrands.co.zw",
        "Founder",
        "Mutasa Brands",
        "CPG",
        "Harare",
        "16 employees",
        "National retailer listing — brand refresh overdue",
        ("cpg", "agency", "brand", "retail"),
    ),
    ProspectSeed(
        "Peter Ndlovu",
        "peter@ndlovuconsult.co.zw",
        "Principal",
        "Ndlovu Operations Consulting",
        "Consulting",
        "Harare",
        "9 employees",
        "Targeting mid-market manufacturers for ops turnarounds",
        ("consulting", "b2b", "manufacturing", "ops"),
    ),
    ProspectSeed(
        "Sarah Chikwanda",
        "sarah@ledgerwise.co.zw",
        "Founder",
        "LedgerWise Accounting",
        "Accounting",
        "Harare",
        "11 employees",
        "Capacity for 20 more SME clients this tax season",
        ("accounting", "sme", "tax", "b2b"),
    ),
    ProspectSeed(
        "Michael Zulu",
        "michael@zuluestate.co.zw",
        "Director",
        "Zulu Commercial Estates",
        "Real estate",
        "Bulawayo",
        "14 employees",
        "Two empty floors downtown after a tenant exit",
        ("commercial_re", "landlord", "office", "leasing"),
    ),
    ProspectSeed(
        "Anita Ferreira",
        "anita@safeguardlegal.co.zw",
        "General Counsel",
        "Safeguard Energy",
        "Energy",
        "Harare",
        "110 employees",
        "Entering a new jurisdiction for a joint venture",
        ("legal", "energy", "compliance", "jv"),
    ),
    ProspectSeed(
        "David Karim",
        "david@karimimports.co.zw",
        "Owner",
        "Karim Imports",
        "Import/Export",
        "Harare",
        "32 employees",
        "Cargo volumes up 40% — cargo and liability gaps likely",
        ("import", "insurance", "fleet", "trade"),
    ),
    ProspectSeed(
        "Precious Dube",
        "precious@growthstack.africa",
        "VP Sales",
        "GrowthStack Africa",
        "B2B SaaS",
        "Harare",
        "50 employees",
        "Building an outbound motion for mid-market SaaS buyers",
        ("saas", "b2b", "sales", "outbound"),
    ),
]


def list_pool() -> list[dict]:
    return [asdict(p) for p in PROSPECT_POOL]


def discover(
    *,
    vertical: str,
    city: str | None = None,
    niche: str | None = None,
    limit: int = 12,
) -> list[ProspectSeed]:
    """Score and return prospects matching an ICP."""
    niche_l = (niche or "").strip().lower()
    city_l = (city or "").strip().lower()
    vertical_l = vertical.strip().lower()

    scored: list[tuple[int, ProspectSeed]] = []
    for p in PROSPECT_POOL:
        score = 0
        tags = {t.lower() for t in p.niche_tags}
        if vertical_l in tags or vertical_l == "b2b":
            score += 5
        if vertical_l == "b2b" and any(t in tags for t in ("b2b", "saas", "agency", "consulting")):
            score += 3
        if city_l and city_l in p.city.lower():
            score += 4
        if niche_l:
            hay = f"{p.company} {p.industry} {p.trigger} {' '.join(p.niche_tags)}".lower()
            if niche_l in hay:
                score += 6
            for token in niche_l.split():
                if token and token in hay:
                    score += 1
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda item: (-item[0], item[1].full_name))
    if not scored:
        # Fallback: return a diverse sample so the pipeline never looks empty.
        return list(PROSPECT_POOL[:limit])
    return [p for _, p in scored[:limit]]
