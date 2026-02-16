import re
from collections.abc import Iterable
from dataclasses import dataclass

import pysolr
from django.conf import settings

_RESERVED_CHARACTERS = (
    "\\",
    "+",
    "-",
    "&&",
    "||",
    "!",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    "^",
    "~",
    "*",
    "?",
    ":",
    "/",
)


def build_search_string(search_string: str | None, field: str | None = None) -> str:
    if search_string is None:
        return "*"

    search_string = search_string.strip()
    if not search_string:
        return "*"

    for char in _RESERVED_CHARACTERS:
        search_string = search_string.replace(char, f"\\{char}")

    def _special_to_lower(match: re.Match[str]) -> str:
        return match.group(0).lower()

    search_string = re.sub(r"\b(OR|AND|NOT)\b", _special_to_lower, search_string)

    exact_matches: list[str] = []
    for literal in re.finditer(r'(")(.+?)(")', search_string):
        value = literal.group(2)
        if field:
            exact_matches.append(f'{field}:"{value}"')
        else:
            exact_matches.append(
                " ".join(
                    (
                        f'name:"{value}"^8 OR',
                        f'description: "{value}"^5 OR',
                        f'email: "{value}" OR',
                        f'external_url: "{value}" OR',
                        f'source_database: "{value}"',
                    )
                )
            )

    search_string = re.sub(r'(".+?")', "", search_string)
    search_string = re.sub(r'"', '\\"', search_string).strip()

    def _build_exact(wild: str, exact: list[str]) -> str:
        if not exact:
            return wild
        exact_string = " AND ".join(exact)
        if not wild:
            return exact_string
        return f"{exact_string} AND ({wild})"

    if not search_string:
        return _build_exact("", exact_matches)

    if field:
        return _build_exact(f"{field}:({search_string})^60", exact_matches)

    wild = (
        f"name:({search_string})^12 OR name_split:({search_string})^6 OR "
        f"description:({search_string})^5 OR description_split:({search_string})^3 OR ({search_string})"
    )
    return _build_exact(wild, exact_matches)


@dataclass(frozen=True)
class SolrHit:
    type: str
    atlas_id: int | None
    id: str | None
    name: str | None
    description: list[str] | None


def _get_solr(url: str, handler: str) -> pysolr.Solr:
    return pysolr.Solr(url, search_handler=handler, timeout=5)


def is_enabled() -> bool:
    return bool(getattr(settings, "SOLR_URL", ""))


def search(handler: str, query: str, *, rows: int = 20, fq: Iterable[str] | None = None) -> list[SolrHit]:
    url = getattr(settings, "SOLR_URL", "")
    if not url:
        return []

    solr = _get_solr(url, handler)
    results = solr.search(query, fq=list(fq or []), **{"rows": rows})

    hits: list[SolrHit] = []
    for doc in results.docs:
        hits.append(
            SolrHit(
                type=str(doc.get("type") or ""),
                atlas_id=doc.get("atlas_id"),
                id=doc.get("id"),
                name=doc.get("name"),
                description=doc.get("description"),
            )
        )
    return hits


def search_reports(q: str, *, rows: int = 20) -> list[SolrHit]:
    return search("reports", build_search_string(q), rows=rows)


def search_terms(q: str, *, rows: int = 20) -> list[SolrHit]:
    return search("aterms", build_search_string(q), rows=rows)
