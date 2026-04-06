import json
import os
from pathlib import Path
from typing import Any

import requests

CATALOG_PATH = Path(__file__).resolve().parent / 'data' / 'remote_catalog.json'


def _load_local_catalog() -> list[dict[str, Any]]:
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_remote_catalog() -> list[dict[str, Any]]:
    """Load remote resource catalog.

    Priority:
    1. REMOTE_RESOURCE_CATALOG_URL env var (remote JSON)
    2. bundled sample catalog for direct local use
    """
    url = os.getenv('REMOTE_RESOURCE_CATALOG_URL', '').strip()
    if url:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
    return _load_local_catalog()


def get_filter_options(catalog: list[dict[str, Any]]) -> dict[str, list[str]]:
    def uniq(key: str):
        return sorted({item.get(key, '') for item in catalog if item.get(key, '')})

    return {
        'countries': uniq('country'),
        'provinces': uniq('province'),
        'grades': uniq('grade'),
        'subjects': uniq('subject'),
    }


def filter_catalog(catalog: list[dict[str, Any]], country: str = '', province: str = '', grade: str = '', subject: str = ''):
    items = catalog
    if country:
        items = [x for x in items if x.get('country') == country]
    if province:
        items = [x for x in items if x.get('province') == province]
    if grade:
        items = [x for x in items if x.get('grade') == grade]
    if subject:
        items = [x for x in items if x.get('subject') == subject]
    return items


def get_topic(catalog: list[dict[str, Any]], topic_id: int):
    for item in catalog:
        if int(item.get('id', -1)) == int(topic_id):
            return item
    return None
