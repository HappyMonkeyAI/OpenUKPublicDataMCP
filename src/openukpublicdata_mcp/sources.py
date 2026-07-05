from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

AuthMode = Literal["none", "optional_key", "required_key"]


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    base_url: str
    docs_url: str
    official: bool
    auth: AuthMode
    coverage: str
    licence: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


SOURCES: dict[str, Source] = {
    "postcodes_io": Source(
        id="postcodes_io",
        name="postcodes.io",
        base_url="https://api.postcodes.io",
        docs_url="https://postcodes.io/docs",
        official=False,
        auth="none",
        coverage="UK postcodes and geodata",
        licence="Open Government Licence / ONSPD-derived data; see upstream",
        notes="Community API using open postcode/geography data.",
    ),
    "govuk_bank_holidays": Source(
        id="govuk_bank_holidays",
        name="GOV.UK Bank Holidays",
        base_url="https://www.gov.uk/bank-holidays.json",
        docs_url="https://github.com/alphagov/frontend/blob/main/docs/calendars.md#calendars",
        official=True,
        auth="none",
        coverage="England and Wales, Scotland, Northern Ireland",
        licence="Open Government Licence where applicable",
    ),
    "govuk_search": Source(
        id="govuk_search",
        name="GOV.UK Search API",
        base_url="https://www.gov.uk/api/search.json",
        docs_url="https://docs.publishing.service.gov.uk/apis/search/search-api.html",
        official=True,
        auth="none",
        coverage="GOV.UK content search",
        licence="Open Government Licence where applicable",
    ),
    "data_gov_uk": Source(
        id="data_gov_uk",
        name="data.gov.uk CKAN API",
        base_url="https://data.gov.uk/api/action",
        docs_url="https://guidance.data.gov.uk/get_data/api_documentation/",
        official=True,
        auth="none",
        coverage="UK public dataset metadata catalogue",
        licence="Dataset-specific; often Open Government Licence",
    ),
    "carbon_intensity": Source(
        id="carbon_intensity",
        name="National Grid ESO Carbon Intensity API",
        base_url="https://api.carbonintensity.org.uk",
        docs_url="https://carbon-intensity.github.io/api-definitions/",
        official=True,
        auth="none",
        coverage="Great Britain electricity carbon intensity",
        licence="See upstream terms",
    ),
    "ea_flood_monitoring": Source(
        id="ea_flood_monitoring",
        name="Environment Agency flood monitoring",
        base_url="https://environment.data.gov.uk/flood-monitoring",
        docs_url="https://environment.data.gov.uk/flood-monitoring/doc/reference",
        official=True,
        auth="none",
        coverage="England flood warnings, areas, and river levels",
        licence="Open Government Licence",
    ),
    "ons_beta_api": Source(
        id="ons_beta_api",
        name="ONS Beta API",
        base_url="https://api.beta.ons.gov.uk/v1",
        docs_url="https://developer.beta.ons.gov.uk/",
        official=True,
        auth="none",
        coverage="ONS datasets, editions, versions, and search",
        licence="Open Government Licence",
    ),
}


def source_metadata(source_id: str) -> dict:
    return SOURCES[source_id].to_dict()
