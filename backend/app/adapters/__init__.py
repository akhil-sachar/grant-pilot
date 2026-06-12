"""Funding source adapters for SponsorAgent opportunity discovery."""

from app.adapters.funding.base import FundingCategory, FundingSourceAdapter, RawFundingRecord
from app.adapters.funding.normalizer import normalize_opportunity
from app.adapters.funding.registry import get_adapter, get_all_adapters

__all__ = [
    "FundingCategory",
    "FundingSourceAdapter",
    "RawFundingRecord",
    "get_adapter",
    "get_all_adapters",
    "normalize_opportunity",
]
