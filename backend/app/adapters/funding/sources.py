from datetime import date, datetime, timezone

from app.adapters.funding.base import FundingCategory, FundingSourceAdapter, RawFundingRecord
from app.adapters.funding.grants_gov_client import fetch_grants_gov_records


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _grants_gov_fallback() -> list[RawFundingRecord]:
    return [
        RawFundingRecord(
            external_id="gov_2026_001",
            source_name="grants_gov",
            category=FundingCategory.FEDERAL_GRANT,
            provider_name="U.S. Department of Education",
            title="Community College STEM Pathways Grant",
            description="Supports community colleges expanding STEM enrollment and transfer pathways.",
            opportunity_type="grant",
            amount_min=250_000,
            amount_max=750_000,
            deadline=date(2026, 9, 30),
            eligibility_summary="Accredited community colleges with demonstrated STEM enrollment growth.",
            requirements=["Project narrative", "Budget justification", "Letters of support"],
            source_url="https://www.grants.gov/search-results-detail/350001",
            tags=["stem", "community-college", "federal"],
            metadata={"live_api": False},
            fetched_at=_now(),
        ),
        RawFundingRecord(
            external_id="gov_2026_002",
            source_name="grants_gov",
            category=FundingCategory.FEDERAL_GRANT,
            provider_name="U.S. Department of Energy",
            title="Clean Energy Workforce Development NOFO",
            description="Funds training programs for clean energy installation and grid modernization careers.",
            opportunity_type="grant",
            amount_min=500_000,
            amount_max=2_000_000,
            deadline=date(2026, 10, 15),
            eligibility_summary="State workforce boards, nonprofits, and accredited training providers.",
            requirements=["Workforce plan", "Partnership MOUs", "Evaluation metrics"],
            source_url="https://www.grants.gov/search-results-detail/350002",
            tags=["clean-energy", "workforce", "federal"],
            metadata={"live_api": False},
            fetched_at=_now(),
        ),
    ]


class GrantsGovAdapter(FundingSourceAdapter):
    source_name = "grants_gov"
    category = FundingCategory.FEDERAL_GRANT

    async def fetch_records(self) -> list[RawFundingRecord]:
        return await fetch_grants_gov_records(_grants_gov_fallback())


class NsfAdapter(FundingSourceAdapter):
    source_name = "nsf"
    category = FundingCategory.RESEARCH_GRANT

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="nsf_2421",
                source_name=self.source_name,
                category=self.category,
                provider_name="National Science Foundation",
                title="NSF REU: Human-Centered AI for Public Services",
                description="Research Experiences for Undergraduates focused on civic AI applications.",
                opportunity_type="fellowship",
                amount_min=8_000,
                amount_max=12_000,
                deadline=date(2026, 7, 20),
                eligibility_summary="Undergraduate students in CS, HCI, or public policy with 3.0+ GPA.",
                requirements=["Faculty nomination", "Research statement", "Transcript"],
                source_url="https://www.nsf.gov/funding/opportunities/reu-hcai",
                tags=["research", "ai", "undergraduate"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="nsf_2422",
                source_name=self.source_name,
                category=self.category,
                provider_name="National Science Foundation",
                title="NSF S-STEM: Computing for Social Impact Scholars",
                description="Scholarships for low-income students pursuing computing degrees with civic projects.",
                opportunity_type="scholarship",
                amount_min=10_000,
                amount_max=15_000,
                deadline=date(2026, 8, 1),
                eligibility_summary="Pell-eligible undergraduates in accredited CS programs.",
                requirements=["FAFSA", "Essay on social impact project", "Faculty reference"],
                source_url="https://www.nsf.gov/funding/opportunities/s-stem-csi",
                tags=["s-stem", "scholarship", "computing"],
                fetched_at=_now(),
            ),
        ]


class NihAdapter(FundingSourceAdapter):
    source_name = "nih"
    category = FundingCategory.HEALTH_RESEARCH

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="nih_r25_001",
                source_name=self.source_name,
                category=self.category,
                provider_name="National Institutes of Health",
                title="NIH R25: Biomedical Data Science Summer Training",
                description="Short-term research training in biomedical informatics and data science.",
                opportunity_type="fellowship",
                amount_min=6_000,
                amount_max=8_500,
                deadline=date(2026, 6, 28),
                eligibility_summary="Undergraduate juniors/seniors interested in biomedical data science.",
                requirements=["Research mentor agreement", "Personal statement", "Transcript"],
                source_url="https://grants.nih.gov/funding/opportunities/r25-biomed-data",
                tags=["biomedical", "data-science", "summer"],
                fetched_at=_now(),
            ),
        ]


class SbirSttrAdapter(FundingSourceAdapter):
    source_name = "sbir_sttr"
    category = FundingCategory.SBIR_STTR

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="sbir_dod_104",
                source_name=self.source_name,
                category=self.category,
                provider_name="U.S. Department of Defense SBIR",
                title="SBIR Phase I: AI-Assisted Grant Discovery Tools",
                description="Seed funding for startups building AI tools that improve access to public funding.",
                opportunity_type="grant",
                amount_min=150_000,
                amount_max=275_000,
                deadline=date(2026, 11, 5),
                eligibility_summary="U.S. small businesses with fewer than 500 employees.",
                requirements=["Technical proposal", "Commercialization plan", "Company registration"],
                source_url="https://www.sbir.gov/node/ai-grant-discovery",
                tags=["sbir", "startup", "ai"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="sbir_nsf_088",
                source_name=self.source_name,
                category=self.category,
                provider_name="NSF SBIR",
                title="STTR: EdTech Platforms for First-Gen Students",
                description="Joint university-industry R&D for student success and scholarship matching platforms.",
                opportunity_type="grant",
                amount_min=256_000,
                amount_max=256_000,
                deadline=date(2026, 12, 1),
                eligibility_summary="Small businesses partnered with a U.S. research institution.",
                requirements=["STTR partnership letter", "Phase I work plan", "Budget"],
                source_url="https://seedfund.nsf.gov/apply/sttr-edtech",
                tags=["sttr", "edtech", "first-gen"],
                fetched_at=_now(),
            ),
        ]


class YcGrantsAdapter(FundingSourceAdapter):
    source_name = "yc_grants"
    category = FundingCategory.STARTUP_GRANT

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="yc_f24_017",
                source_name=self.source_name,
                category=self.category,
                provider_name="Y Combinator",
                title="YC Nonprofit Grant: Access to Opportunity Tech",
                description="$50K grants for nonprofits using software to expand education and funding access.",
                opportunity_type="grant",
                amount_min=50_000,
                amount_max=50_000,
                deadline=date(2026, 7, 15),
                eligibility_summary="501(c)(3) nonprofits with a working product and measurable impact.",
                requirements=["Demo link", "Impact metrics", "Team bios"],
                source_url="https://www.ycombinator.com/grants/nonprofit",
                tags=["nonprofit", "yc", "startup"],
                fetched_at=_now(),
            ),
        ]


class FoundationDirectoriesAdapter(FundingSourceAdapter):
    source_name = "foundation_directories"
    category = FundingCategory.FOUNDATION

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="fd_gates_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Gates Foundation",
                title="Digital Equity in Higher Education Fund",
                description="Foundation grants for tools that reduce friction in financial aid and scholarship access.",
                opportunity_type="grant",
                amount_min=100_000,
                amount_max=500_000,
                deadline=date(2026, 8, 30),
                eligibility_summary="Nonprofits and public institutions serving underrepresented students.",
                requirements=["Theory of change", "Equity impact plan", "Budget"],
                source_url="https://www.gatesfoundation.org/grants/digital-equity-he",
                tags=["foundation", "equity", "higher-ed"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="fd_knight_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Knight Foundation",
                title="Civic Tech Innovation Award",
                description="Awards for open-source civic technology improving local government transparency.",
                opportunity_type="award",
                amount_min=25_000,
                amount_max=75_000,
                deadline=date(2026, 9, 10),
                eligibility_summary="Teams with deployed civic tech projects in U.S. communities.",
                requirements=["Project demo", "Community impact story", "Open-source repository"],
                source_url="https://knightfoundation.org/grants/civic-tech-innovation",
                tags=["civic-tech", "open-source", "award"],
                fetched_at=_now(),
            ),
        ]


class UniversityGrantsAdapter(FundingSourceAdapter):
    source_name = "university_grants"
    category = FundingCategory.UNIVERSITY

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="ucb_urap_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="UC Berkeley Undergraduate Research",
                title="URAP Civic Data Fellowship",
                description="Campus-funded fellowship for undergraduates researching open government data systems.",
                opportunity_type="fellowship",
                amount_min=3_500,
                amount_max=5_000,
                deadline=date(2026, 7, 1),
                eligibility_summary="UC Berkeley undergraduates with faculty sponsor.",
                requirements=["Faculty sponsor form", "Research proposal", "Transcript"],
                source_url="https://research.berkeley.edu/urap/civic-data",
                tags=["university", "research", "fellowship"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="mit_pkg_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="MIT PKG Center",
                title="Public Service Innovation Grant",
                description="Micro-grants for student-led public service technology projects.",
                opportunity_type="grant",
                amount_min=1_000,
                amount_max=5_000,
                deadline=date(2026, 10, 1),
                eligibility_summary="MIT students with a faculty or community partner.",
                requirements=["Project plan", "Community partner letter", "Budget"],
                source_url="https://pkgcenter.mit.edu/grants/innovation",
                tags=["university", "public-service", "student-led"],
                fetched_at=_now(),
            ),
        ]


class ScholarshipsAdapter(FundingSourceAdapter):
    source_name = "scholarships"
    category = FundingCategory.SCHOLARSHIP

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="sch_coca_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Coca-Cola Scholars Foundation",
                title="Coca-Cola First-Generation Leaders Scholarship",
                description="Merit scholarship for first-generation college students demonstrating leadership.",
                opportunity_type="scholarship",
                amount_min=5_000,
                amount_max=20_000,
                deadline=date(2026, 8, 15),
                eligibility_summary="First-generation U.S. high school seniors and college freshmen.",
                requirements=["Application essay", "Leadership resume", "Transcript"],
                source_url="https://www.coca-colascholarsfoundation.org/apply",
                tags=["first-gen", "leadership", "merit"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="sch_jack_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Jack Kent Cooke Foundation",
                title="Cooke Undergraduate Transfer Scholarship",
                description="Full-ride scholarship for community college students transferring to four-year institutions.",
                opportunity_type="scholarship",
                amount_min=40_000,
                amount_max=55_000,
                deadline=date(2026, 9, 1),
                eligibility_summary="Community college students with 3.5+ GPA transferring in fall 2027.",
                requirements=["Financial need documentation", "Essays", "Counselor recommendation"],
                source_url="https://www.jkcf.org/our-scholarships/undergraduate-transfer-scholarship/",
                tags=["transfer", "full-ride", "community-college"],
                fetched_at=_now(),
            ),
        ]


class CorporateInnovationAdapter(FundingSourceAdapter):
    source_name = "corporate_innovation"
    category = FundingCategory.CORPORATE

    async def fetch_records(self) -> list[RawFundingRecord]:
        return [
            RawFundingRecord(
                external_id="corp_google_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Google.org",
                title="AI for Social Good Innovation Fund",
                description="Corporate innovation fund for nonprofits and social enterprises using AI responsibly.",
                opportunity_type="grant",
                amount_min=250_000,
                amount_max=1_000_000,
                deadline=date(2026, 11, 20),
                eligibility_summary="Registered nonprofits with AI prototypes serving underserved communities.",
                requirements=["Impact proposal", "Responsible AI plan", "Pilot metrics"],
                source_url="https://www.google.org/ai-social-good",
                tags=["corporate", "ai", "social-impact"],
                fetched_at=_now(),
            ),
            RawFundingRecord(
                external_id="corp_msft_2026",
                source_name=self.source_name,
                category=self.category,
                provider_name="Microsoft AI for Good",
                title="Azure Credits + Cash Grant for EdTech Startups",
                description="Hybrid funding package for early-stage edtech companies improving student outcomes.",
                opportunity_type="grant",
                amount_min=50_000,
                amount_max=150_000,
                deadline=date(2026, 10, 30),
                eligibility_summary="Seed-stage startups with an MVP and at least one pilot school.",
                requirements=["Pitch deck", "Pilot results", "Technical architecture"],
                source_url="https://www.microsoft.com/en-us/ai/ai-for-good/edtech",
                tags=["corporate", "edtech", "azure"],
                fetched_at=_now(),
            ),
        ]
