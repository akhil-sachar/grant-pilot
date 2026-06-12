from app.adapters.funding.base import FundingSourceAdapter
from app.adapters.funding.sources import (
    CorporateInnovationAdapter,
    FoundationDirectoriesAdapter,
    GrantsGovAdapter,
    NihAdapter,
    NsfAdapter,
    SbirSttrAdapter,
    ScholarshipsAdapter,
    UniversityGrantsAdapter,
    YcGrantsAdapter,
)


def get_all_adapters() -> list[FundingSourceAdapter]:
    return [
        GrantsGovAdapter(),
        NsfAdapter(),
        NihAdapter(),
        SbirSttrAdapter(),
        YcGrantsAdapter(),
        FoundationDirectoriesAdapter(),
        UniversityGrantsAdapter(),
        ScholarshipsAdapter(),
        CorporateInnovationAdapter(),
    ]


def get_adapter(source_name: str) -> FundingSourceAdapter | None:
    for adapter in get_all_adapters():
        if adapter.source_name == source_name:
            return adapter
    return None
