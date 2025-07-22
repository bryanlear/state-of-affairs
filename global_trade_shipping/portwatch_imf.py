#!/usr/bin/env python3
"""
portwatch_fetch.py
==================
Utility functions and a simple CLI for downloading the **PortWatch** open-data layers that track
worldwide maritime trade.

It covers three datasets that the IMF currently publishes via its ArcGIS Hub portal:

1. **Daily Port Activity Data and Trade Estimates**  (item-id ``959214444157458aad969389b3ebe1a0``)
2. **Daily Chokepoint Transit Calls and Trade Volume Estimates** (item-id ``42132aa4e2fc4d41bdaf9a445f688931``)
3. **Ports & Chokepoints reference layers**
   * ports – ``acc668d199d1472abaaf2467133d4ca4``  
   * chokepoints – ``fa9a5800b0ee4855af8b2944ab1e07af``

The script discovers each item’s FeatureServer URL on-the-fly via the public ArcGIS REST API and
paginates through the layer so you don’t have to worry about 2000-record limits.

Usage
-----
```bash
$ pip install pandas requests
$ python portwatch_fetch.py                # dumps four CSVs in the current dir

# Custom date range & filter examples:
$ python - <<'PY'
from portwatch_fetch import get_port_activity
# Rotterdam, Antwerp-Bruges, Hamburg only (portid 655, 658, 660)
print(get_port_activity('2024-07-01', '2025-06-30', port_ids=[655,658,660]).head())
PY
```
"""
import datetime as _dt
from pathlib import Path as _P
from typing import List, Optional

import pandas as _pd
import requests as _r

_ARCGIS_PORTAL = "https://www.arcgis.com"

_DATASETS = {
    "port_activity": "959214444157458aad969389b3ebe1a0",   # Daily Port Activity Data
    "chokepoint_daily": "42132aa4e2fc4d41bdaf9a445f688931",  # Daily Chokepoint Transit Data
    "ports_meta": "acc668d199d1472abaaf2467133d4ca4",       # Ports reference layer
    "chokepoints_meta": "fa9a5800b0ee4855af8b2944ab1e07af"   # Chokepoints reference layer
}

###############################################################################
# Low-level helpers                                                            #
###############################################################################

def _item_info(item_id: str) -> dict:
    """Return the ArcGIS item metadata as a JSON dict."""
    resp = _r.get(f"{_ARCGIS_PORTAL}/sharing/rest/content/items/{item_id}", params={"f": "json"})
    resp.raise_for_status()
    return resp.json()


def _service_url(item_id: str) -> str:
    """Extract the FeatureServer base URL from an item-id."""
    meta = _item_info(item_id)
    if "url" not in meta:
        raise RuntimeError(f"Item {item_id} has no public service URL – is it shared?")
    return meta["url"].rstrip("/")  # e.g. …/FeatureServer


def _query(service_url: str, layer: int = 0, where: str = "1=1", *,
           out_fields: str = "*", batch_size: int = 2000,
           token: Optional[str] = None) -> _pd.DataFrame:
    """Download *all* rows that satisfy *where* from a FeatureServer layer."""
    endpoint = f"{service_url}/{layer}/query"
    params = {
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "false",
        "f": "json",
        "resultOffset": 0,
        "resultRecordCount": batch_size,
    }
    if token:
        params["token"] = token

    records = []
    while True:
        r = _r.get(endpoint, params=params, timeout=120)
        r.raise_for_status()
        j = r.json()
        if "error" in j:
            raise RuntimeError(j["error"])
        batch = [ft["attributes"] for ft in j.get("features", [])]
        if not batch:
            break
        records.extend(batch)
        if len(batch) < batch_size:
            break
        params["resultOffset"] += batch_size
    return _pd.DataFrame.from_records(records)

###############################################################################
# (w)Rappers                                                  #
###############################################################################

def get_port_activity(start_date: str, end_date: str, *,
                      port_ids: Optional[List[int]] = None,
                      include_estimates: bool = True) -> _pd.DataFrame:
    """Return Daily Port Activity rows between *start_date* and *end_date* (YYYY-MM-DD)."""
    service = _service_url(_DATASETS["port_activity"])
    where = f"day >= DATE '{start_date}' AND day <= DATE '{end_date}'"
    if port_ids:
        where += f" AND portid IN ({','.join(map(str, port_ids))})"
    if not include_estimates:
        where += " AND (export_tons IS NOT NULL OR import_tons IS NOT NULL)"
    return _query(service, where=where)


def get_chokepoint_transit(start_date: str, end_date: str, *,
                           chokepoint_ids: Optional[List[int]] = None) -> _pd.DataFrame:
    service = _service_url(_DATASETS["chokepoint_daily"])
    where = f"day >= DATE '{start_date}' AND day <= DATE '{end_date}'"
    if chokepoint_ids:
        where += f" AND chokepointid IN ({','.join(map(str, chokepoint_ids))})"
    return _query(service, where=where)


def get_ports_metadata(*, relevant_only: bool = True) -> _pd.DataFrame:
    service = _service_url(_DATASETS["ports_meta"])
    where = "is_relevant = 1" if relevant_only else "1=1"
    return _query(service, where=where)


def get_chokepoints_metadata() -> _pd.DataFrame:
    service = _service_url(_DATASETS["chokepoints_meta"])
    return _query(service, where="1=1")

###############################################################################
# Simple CLI                                               
###############################################################################

def _dump_csv(df: _pd.DataFrame, filename: str):
    fp = _P(filename)
    df.to_csv(fp, index=False)
    print(f"[✓] wrote {len(df):,} rows → {fp.resolve()}")


def main():
    today = _dt.date.today()
    start = (today - _dt.timedelta(days=365)).isoformat()
    end = today.isoformat()

    print("Fetching Daily Port Activity …")
    _dump_csv(get_port_activity(start, end), "port_activity_last_year.csv")

    print("Fetching Daily Chokepoint Transit …")
    _dump_csv(get_chokepoint_transit(start, end), "chokepoint_transit_last_year.csv")

    print("Fetching Ports metadata …")
    _dump_csv(get_ports_metadata(), "ports_metadata.csv")

    print("Fetching Chokepoints metadata …")
    _dump_csv(get_chokepoints_metadata(), "chokepoints_metadata.csv")


if __name__ == "__main__":
    main()
