from __future__ import annotations

import os
import time
from typing import Any, Sequence

import requests

from .exceptions import (
    AuthenticationError,
    LookupRunError,
    LookupTimeoutError,
    SantoFindsError,
)

ACTOR_ID = "apivault_labs~skip-trace-people-finder"
APIFY_API_BASE = "https://api.apify.com/v2"
TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}
VALID_TIERS = ("basic", "premium")
PRICE_PER_RESULT_USD = {"basic": 0.007, "premium": 0.015}


class SantoFindsClient:
    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 900,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError("APIFY_API_TOKEN is required")
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be greater than 0")
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "santofinds-python/0.2.0",
        })
        self._last_run_id: str | None = None
        self._last_dataset_id: str | None = None

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "SantoFindsClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def search(
        self,
        *,
        names: Sequence[str] = (),
        addresses: Sequence[str] = (),
        phones: Sequence[str] = (),
        tier: str = "basic",
        max_results: int = 5,
        use_residential: bool = True,
        max_concurrency: int = 4,
        max_retries: int = 2,
        timeout_per_request: int = 25,
        actor_timeout_secs: int = 600,
    ) -> list[dict[str, Any]]:
        clean_names = [n.strip() for n in names if n and n.strip()]
        clean_addresses = [a.strip() for a in addresses if a and a.strip()]
        clean_phones = [p.strip() for p in phones if p and p.strip()]
        if not (clean_names or clean_addresses or clean_phones):
            raise ValueError("Provide at least one search input")
        if tier not in VALID_TIERS:
            raise ValueError(f"tier must be one of {VALID_TIERS}")
        if actor_timeout_secs <= 0:
            raise ValueError("actor_timeout_secs must be greater than 0")

        payload: dict[str, Any] = {
            "tier": tier,
            "max_results": max(1, min(20, int(max_results))),
            "useResidential": bool(use_residential),
            "maxConcurrency": max(1, min(8, int(max_concurrency))),
            "maxRetries": max(0, min(3, int(max_retries))),
            "timeout": max(10, min(45, int(timeout_per_request))),
        }
        if clean_names:
            payload["name"] = clean_names
        if clean_addresses:
            payload["street_citystatezip"] = clean_addresses
        if clean_phones:
            payload["phone_number"] = clean_phones

        run_id = self._start_run(payload, actor_timeout_secs)
        run = self._wait_for_run(run_id)
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            raise LookupRunError("Apify response did not include a dataset id")
        self._last_run_id = run_id
        self._last_dataset_id = dataset_id
        return self._fetch_dataset(dataset_id)

    def search_by_name(self, *names: str, tier: str = "basic", max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(names=names, tier=tier, max_results=max_results, **kwargs)

    def search_by_address(self, *addresses: str, tier: str = "basic", max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(addresses=addresses, tier=tier, max_results=max_results, **kwargs)

    def search_by_phone(self, *phones: str, tier: str = "basic", max_results: int = 5, **kwargs: Any) -> list[dict[str, Any]]:
        return self.search(phones=phones, tier=tier, max_results=max_results, **kwargs)

    def filter_with_phone(self, people: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [p for p in people if p.get("phones") or p.get("phone")]

    def filter_with_email(self, people: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [p for p in people if p.get("emails") or p.get("email")]

    def filter_by_min_age(self, people: Sequence[dict[str, Any]], min_age: int) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for person in people:
            try:
                if int(person.get("age") or 0) >= min_age:
                    out.append(person)
            except (TypeError, ValueError):
                continue
        return out

    def filter_by_state(self, people: Sequence[dict[str, Any]], *states: str) -> list[dict[str, Any]]:
        wanted = {state.strip().upper() for state in states if state and state.strip()}
        if not wanted:
            return list(people)
        out: list[dict[str, Any]] = []
        for person in people:
            address = str(person.get("currentAddress") or person.get("address") or "").upper()
            if any(f" {state} " in f" {address} " or address.endswith(f" {state}") or f", {state}" in address for state in wanted):
                out.append(person)
        return out

    def best_phone(self, person: dict[str, Any]) -> str | None:
        phones = person.get("phones")
        if isinstance(phones, list) and phones:
            first = phones[0]
            if isinstance(first, dict):
                return first.get("number") or first.get("phone")
            return str(first)
        return person.get("phone")

    def estimate_cost(self, expected_results: int, tier: str = "basic") -> float:
        if tier not in VALID_TIERS:
            raise ValueError(f"tier must be one of {VALID_TIERS}")
        if expected_results < 0:
            raise ValueError("expected_results must not be negative")
        return round(expected_results * PRICE_PER_RESULT_USD[tier], 4)

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        try:
            response = self._session.post(url, params={"timeout": int(actor_timeout_secs)}, json=payload, timeout=30)
        except requests.RequestException as exc:
            raise SantoFindsError(f"Failed to start lookup: {exc}") from exc
        if response.status_code == 401:
            raise AuthenticationError("Apify rejected the API token")
        if response.status_code >= 400:
            raise LookupRunError(f"Apify returned HTTP {response.status_code}: {response.text[:300]}")
        try:
            data = response.json().get("data") or {}
        except ValueError as exc:
            raise LookupRunError("Apify returned invalid JSON") from exc
        run_id = data.get("id")
        if not run_id:
            raise LookupRunError("Apify response missing run id")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                response = self._session.get(url, timeout=30)
            except requests.RequestException as exc:
                raise SantoFindsError(f"Failed to poll lookup: {exc}") from exc
            if response.status_code >= 400:
                raise LookupRunError(f"Apify returned HTTP {response.status_code}: {response.text[:300]}")
            try:
                run = response.json().get("data") or {}
            except ValueError as exc:
                raise LookupRunError("Apify returned invalid JSON") from exc
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise LookupRunError(f"Lookup run ended with status={status}: {run.get('statusMessage') or 'no message'}")
            if time.time() > deadline:
                raise LookupTimeoutError(f"Lookup run {run_id} did not finish within {self._timeout}s")
            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        try:
            response = self._session.get(url, params={"clean": "true", "format": "json"}, timeout=120)
        except requests.RequestException as exc:
            raise SantoFindsError(f"Failed to download lookup results: {exc}") from exc
        if response.status_code >= 400:
            raise LookupRunError(f"Apify returned HTTP {response.status_code}: {response.text[:300]}")
        try:
            data = response.json()
        except ValueError as exc:
            raise LookupRunError("Apify dataset is not valid JSON") from exc
        if not isinstance(data, list):
            raise LookupRunError(f"Unexpected dataset payload: {type(data).__name__}")
        return data
