#!/usr/bin/env python3
"""
High-performance async SERP data exporter for DataForSEO API.

Optimized for processing large batches (2000+ keywords) with:
- Concurrent async HTTP requests (configurable concurrency)
- Connection pooling and keep-alive
- Automatic retries with exponential backoff
- Progress reporting
- Graceful error handling
"""

import asyncio
import aiohttp
import base64
import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configuration
ROOT_DIR = Path(__file__).resolve().parent
KEYWORDS_FILE = ROOT_DIR / "inputs" / "keywords.txt"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# API Settings
API_BASE_URL = "https://api.dataforseo.com/v3"
LOCATION_CODE = 9189292
LANGUAGE_CODE = "en"
DEVICE = "desktop"
OS = "macos"
DEPTH = 20
LOAD_ASYNC_AI_OVERVIEW = True
LOAD_GOOGLE_AI_MODE = True  # Enable Google AI Mode endpoint queries

# Performance tuning - adjust based on your API plan limits
MAX_CONCURRENT_REQUESTS = 20  # Number of simultaneous API requests
REQUEST_TIMEOUT = 60  # Seconds per request
MAX_RETRIES = 3  # Retry failed requests
RETRY_DELAY_BASE = 1.0  # Base delay for exponential backoff (seconds)


@dataclass
class ProcessingStats:
    """Track processing statistics."""
    total: int = 0
    completed: int = 0
    failed: int = 0
    ai_overview_rows: int = 0
    organic_rows: int = 0
    ai_mode_rows: int = 0

    def print_progress(self) -> None:
        """Print current progress."""
        pct = (self.completed + self.failed) / self.total * 100 if self.total else 0
        print(
            f"\rProgress: {self.completed + self.failed}/{self.total} ({pct:.1f}%) "
            f"| Success: {self.completed} | Failed: {self.failed} "
            f"| AI Overview: {self.ai_overview_rows} | Organic: {self.organic_rows} "
            f"| AI Mode: {self.ai_mode_rows}",
            end="",
            flush=True,
        )


# CSV field names
UNIFIED_FIELDNAMES = [
    "result_type",
    "keyword",
    "domain",
    "page",
    "rank_group",
    "rank_absolute",
    "position",
    "url",
    "title",
    "description",
    "extended_snippet",
    "breadcrumb",
    "website_name",
    "references_source",
    "references_url",
    "references_text",
    "references_markdown",
    # AI Mode-specific fields
    "ai_mode_summary",
    "ai_mode_citations_count",
    "ai_mode_primary_domain",
    "ai_mode_primary_url",
]


def _load_keywords(path: Path) -> List[str]:
    """Load keywords from file."""
    if not path.exists():
        print(f"Keywords file not found: {path}", file=sys.stderr)
        return []
    keywords: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            kw = line.strip()
            if kw:
                keywords.append(kw)
    return keywords


def _create_output_paths() -> Tuple[Path, Path]:
    """Create the output CSV and JSON file paths with timestamp."""
    csv_dir = OUTPUTS_DIR / "csv"
    json_dir = OUTPUTS_DIR / "json"
    csv_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return csv_dir / f"serp_results_{ts}.csv", json_dir / f"serp_results_{ts}.json"


def _extract_ai_overview_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract AI Overview reference rows suitable for CSV."""
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                if item.get("type") != "ai_overview":
                    continue

                ai_markdown = item.get("markdown")

                for ref in item.get("references") or []:
                    rows.append({
                        "result_type": "ai_overview",
                        "keyword": result_keyword,
                        "domain": ref.get("domain"),
                        "references_source": ref.get("source") or ref.get("title"),
                        "references_url": ref.get("url"),
                        "references_text": ref.get("text"),
                        "references_markdown": ai_markdown or "",
                    })

                for sub_item in item.get("items") or []:
                    sub_markdown = sub_item.get("markdown") or ai_markdown or ""

                    for ref in sub_item.get("references") or []:
                        rows.append({
                            "result_type": "ai_overview",
                            "keyword": result_keyword,
                            "domain": ref.get("domain"),
                            "references_source": ref.get("source") or ref.get("title"),
                            "references_url": ref.get("url"),
                            "references_text": ref.get("text"),
                            "references_markdown": sub_markdown,
                        })

                    for component in sub_item.get("components") or []:
                        comp_markdown = component.get("markdown") or sub_markdown
                        for ref in component.get("references") or []:
                            rows.append({
                                "result_type": "ai_overview",
                                "keyword": result_keyword,
                                "domain": ref.get("domain"),
                                "references_source": ref.get("source") or ref.get("title"),
                                "references_url": ref.get("url"),
                                "references_text": ref.get("text"),
                                "references_markdown": comp_markdown or "",
                            })

    return rows


def _extract_organic_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract organic result rows suitable for CSV."""
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                if item.get("type") != "organic":
                    continue

                rows.append({
                    "result_type": "organic",
                    "keyword": result_keyword,
                    "page": item.get("page"),
                    "rank_group": item.get("rank_group"),
                    "rank_absolute": item.get("rank_absolute"),
                    "position": item.get("position"),
                    "domain": item.get("domain"),
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "extended_snippet": item.get("extended_snippet"),
                    "breadcrumb": item.get("breadcrumb"),
                    "website_name": item.get("website_name"),
                })

    return rows


def _extract_ai_mode_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract Google AI Mode rows suitable for CSV.
    
    Creates one row per AI Mode response, capturing the summary markdown,
    citation count, and primary citation details.
    """
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                item_type = item.get("type")
                # AI Mode returns items with type "ai_overview"
                if item_type != "ai_overview":
                    continue

                ai_markdown = item.get("markdown") or ""
                references = item.get("references") or []
                citations_count = len(references)

                # Determine primary citation (first reference if available)
                primary_domain = ""
                primary_url = ""
                if references:
                    first_ref = references[0]
                    primary_domain = first_ref.get("domain") or ""
                    primary_url = first_ref.get("url") or ""

                # Create one row per AI Mode overview
                rows.append({
                    "result_type": "ai_mode",
                    "keyword": result_keyword,
                    "ai_mode_summary": ai_markdown,
                    "ai_mode_citations_count": citations_count,
                    "ai_mode_primary_domain": primary_domain,
                    "ai_mode_primary_url": primary_url,
                    "domain": primary_domain,  # Also populate shared domain field
                })

                # Additionally, create rows for each reference to capture citation details
                for ref in references:
                    rows.append({
                        "result_type": "ai_mode",
                        "keyword": result_keyword,
                        "domain": ref.get("domain"),
                        "references_source": ref.get("source") or ref.get("title"),
                        "references_url": ref.get("url"),
                        "references_text": ref.get("text"),
                        "references_markdown": ai_markdown,
                        "ai_mode_summary": "",  # Summary only on main row
                        "ai_mode_citations_count": "",
                        "ai_mode_primary_domain": "",
                        "ai_mode_primary_url": "",
                    })

    return rows


def _write_unified_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write all rows to a single unified CSV file."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=UNIFIED_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in UNIFIED_FIELDNAMES})


def _write_json(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Write all rows to a JSON file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


async def fetch_serp_data(
    session: aiohttp.ClientSession,
    keyword: str,
    auth_header: str,
    semaphore: asyncio.Semaphore,
    stats: ProcessingStats,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Fetch SERP data for a single keyword with retry logic.
    
    Returns (keyword, response_dict) or (keyword, None) on failure.
    """
    url = f"{API_BASE_URL}/serp/google/organic/live/advanced"
    
    payload = [{
        "keyword": keyword,
        "location_code": LOCATION_CODE,
        "language_code": LANGUAGE_CODE,
        "device": DEVICE,
        "os": OS,
        "depth": DEPTH,
        "load_async_ai_overview": LOAD_ASYNC_AI_OVERVIEW,
    }]
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    
    async with semaphore:  # Limit concurrent requests
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return (keyword, data)
                    elif response.status == 429:  # Rate limited
                        delay = RETRY_DELAY_BASE * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        error_text = await response.text()
                        print(f"\nAPI error for '{keyword}': {response.status} - {error_text[:200]}", file=sys.stderr)
                        return (keyword, None)
                        
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                print(f"\nTimeout for keyword '{keyword}' after {MAX_RETRIES} attempts", file=sys.stderr)
                return (keyword, None)
                
            except aiohttp.ClientError as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                print(f"\nConnection error for '{keyword}': {e}", file=sys.stderr)
                return (keyword, None)
    
    return (keyword, None)


async def fetch_ai_mode_data(
    session: aiohttp.ClientSession,
    keyword: str,
    auth_header: str,
    semaphore: asyncio.Semaphore,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Fetch Google AI Mode data for a single keyword with retry logic.
    
    Returns (keyword, response_dict) or (keyword, None) on failure.
    """
    url = f"{API_BASE_URL}/serp/google/ai_mode/live/advanced"
    
    payload = [{
        "keyword": keyword,
        "location_code": LOCATION_CODE,
        "language_code": LANGUAGE_CODE,
    }]
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    
    async with semaphore:  # Limit concurrent requests
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return (keyword, data)
                    elif response.status == 429:  # Rate limited
                        delay = RETRY_DELAY_BASE * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        error_text = await response.text()
                        print(f"\nAI Mode API error for '{keyword}': {response.status} - {error_text[:200]}", file=sys.stderr)
                        return (keyword, None)
                        
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                print(f"\nAI Mode timeout for keyword '{keyword}' after {MAX_RETRIES} attempts", file=sys.stderr)
                return (keyword, None)
                
            except aiohttp.ClientError as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                print(f"\nAI Mode connection error for '{keyword}': {e}", file=sys.stderr)
                return (keyword, None)
    
    return (keyword, None)


async def process_single_keyword(
    session: aiohttp.ClientSession,
    keyword: str,
    auth_header: str,
    semaphore: asyncio.Semaphore,
    stats: ProcessingStats,
) -> List[Dict[str, Any]]:
    """
    Process a single keyword: fetch SERP data and optionally AI Mode data.
    Returns all extracted rows for this keyword.
    """
    rows: List[Dict[str, Any]] = []
    
    # Fetch SERP data (organic + AI overview)
    _, serp_response = await fetch_serp_data(session, keyword, auth_header, semaphore, stats)
    
    if serp_response:
        ai_overview_rows = _extract_ai_overview_rows(serp_response, keyword)
        organic_rows = _extract_organic_rows(serp_response, keyword)
        rows.extend(ai_overview_rows)
        rows.extend(organic_rows)
        
        stats.ai_overview_rows += len(ai_overview_rows)
        stats.organic_rows += len(organic_rows)
        
        # Fetch AI Mode data if enabled
        if LOAD_GOOGLE_AI_MODE:
            _, ai_mode_response = await fetch_ai_mode_data(session, keyword, auth_header, semaphore)
            if ai_mode_response:
                ai_mode_rows = _extract_ai_mode_rows(ai_mode_response, keyword)
                rows.extend(ai_mode_rows)
                stats.ai_mode_rows += len(ai_mode_rows)
        
        stats.completed += 1
    else:
        stats.failed += 1
    
    return rows


async def process_keywords_async(
    keywords: List[str],
    username: str,
    password: str,
) -> List[Dict[str, Any]]:
    """
    Process all keywords concurrently and return collected rows.
    """
    # Create Basic Auth header
    credentials = f"{username}:{password}"
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Stats tracking
    stats = ProcessingStats(total=len(keywords))
    
    # Configure connection pooling
    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT_REQUESTS,
        limit_per_host=MAX_CONCURRENT_REQUESTS,
        keepalive_timeout=30,
        enable_cleanup_closed=True,
    )
    
    all_rows: List[Dict[str, Any]] = []
    
    ai_mode_status = "enabled" if LOAD_GOOGLE_AI_MODE else "disabled"
    print(f"Processing {len(keywords)} keywords with {MAX_CONCURRENT_REQUESTS} concurrent requests...")
    print(f"Google AI Mode: {ai_mode_status}")
    print()
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create tasks for all keywords
        tasks = [
            process_single_keyword(session, kw, auth_header, semaphore, stats)
            for kw in keywords
        ]
        
        # Process with progress updates
        for coro in asyncio.as_completed(tasks):
            keyword_rows = await coro
            all_rows.extend(keyword_rows)
            stats.print_progress()
    
    print()  # New line after progress
    return all_rows


def main() -> int:
    """Main entry point."""
    username = "dan@perth-seo-agency.com.au"
    password = "bf723abcdd2effb0"

    keywords = _load_keywords(KEYWORDS_FILE)
    if not keywords:
        print("No keywords found in inputs/keywords.txt", file=sys.stderr)
        return 1

    print(f"Loaded {len(keywords)} keywords from {KEYWORDS_FILE}")
    print(f"Configuration: {MAX_CONCURRENT_REQUESTS} concurrent requests, {REQUEST_TIMEOUT}s timeout")
    print()

    # Run async processing
    start_time = dt.datetime.now()
    all_rows = asyncio.run(process_keywords_async(keywords, username, password))
    elapsed = dt.datetime.now() - start_time

    # Write results
    csv_path, json_path = _create_output_paths()
    _write_unified_csv(csv_path, all_rows)
    _write_json(json_path, all_rows)
    
    print()
    print(f"=" * 60)
    print(f"Completed in {elapsed.total_seconds():.1f} seconds")
    print(f"Wrote {len(all_rows)} total rows to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"Average: {len(keywords) / elapsed.total_seconds():.1f} keywords/second")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
