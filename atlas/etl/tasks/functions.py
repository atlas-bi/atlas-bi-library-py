"""Functions shared between ETL steps."""
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union

import pytz


def chunker(seq: List[Any], size: int) -> Generator[List[Any], None, None]:
    """Split big list into parts.

    https://stackoverflow.com/a/434328/10265880
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))  # noqa: E203


def clean_doc(doc: Dict[Any, Any]) -> Dict[Any, Any]:
    """Clean up a solr doc list."""

    def clean_list(my_list: Union[List[Any], Any]) -> Union[List[Any], Any]:
        """Remove None and "None" values from a list."""
        if not isinstance(my_list, list):
            return my_list

        return [i for i in my_list if i and i != "None"] or None

    return {
        k: clean_list(v) for k, v in doc.items() if clean_list(v) not in [None, "None"]
    }


def solr_date(date: Union[datetime, Any]) -> Optional[str]:
    """Convert datetime to solr date format."""
    if isinstance(date, datetime):
        return datetime.strftime(
            date.astimezone(pytz.utc),
            "%Y-%m-%dT%H:%M:%SZ",
        )

    return None
