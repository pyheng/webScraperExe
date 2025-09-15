#!/usr/bin/env python3
"""
site_searcher.py
Usage examples:
  python site_searcher.py --url "https://example.com" --selector "a" --attr "href" --output results.csv
  python site_searcher.py --url "https://example.com" --xpath "//div[@class='post']" --text --output results.json
  python site_searcher.py --url "https://example.com" --selector ".item" --attr "data-id" --headless --output results.csv

Notes:
- For static pages, the default requests/BeautifulSoup method is fastest.
- If the page requires JS, pass --headless (requires selenium and a browser driver or webdriver-manager).
"""

import argparse
import json
import csv
import sys
from typing import List
from urllib.parse import urljoin

# Requests & BeautifulSoup approach (static pages)
import requests
from bs4 import BeautifulSoup

# Selenium optional import (only if user requests headless)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


def fetch_static(url: str, timeout=15) -> str:
    headers = {
        "User-Agent": "SiteSearcher/1.0 (+https://example.com)"
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def fetch_with_selenium(url: str, timeout=30, headless=True) -> str:
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium or webdriver-manager not installed. Install requirements or run without --headless.")
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_page_load_timeout(timeout)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def parse_with_selector(html: str, selector: str, base_url: str, attr: str=None, text: bool=False) -> List[dict]:
    soup = BeautifulSoup(html, "lxml")
    elems = soup.select(selector)
    out = []
    for el in elems:
        item = {}
        if text:
            item["text"] = el.get_text(strip=True)
        if attr:
            val = el.get(attr)
            if val and base_url:
                # convert relative URLs to absolute
                if attr in ("href", "src"):
                    val = urljoin(base_url, val)
            item[attr if attr else "value"] = val
        # also provide html snippet and tag for flexibility
        item["tag"] = el.name
        item["html"] = str(el)[:1000]  # cap length
        out.append(item)
    return out

def parse_with_xpath(html: str, xpath: str, base_url: str, attr: str=None, text: bool=False) -> List[dict]:
    # use lxml for xpath
    from lxml import etree, html as lxml_html
    doc = lxml_html.fromstring(html)
    nodes = doc.xpath(xpath)
    out = []
    for n in nodes:
        item = {}
        if isinstance(n, etree._ElementUnicodeResult) or isinstance(n, str):
            item["text"] = str(n)
            out.append(item)
            continue
        if text:
            item["text"] = "".join(n.itertext()).strip()
        if attr:
            val = n.get(attr)
            if val and base_url:
                if attr in ("href", "src"):
                    val = urljoin(base_url, val)
            item[attr if attr else "value"] = val
        item["tag"] = n.tag
        item["html"] = lxml_html.tostring(n, encoding="unicode")[:1000]
        out.append(item)
    return out

def save_output(items: List[dict], output_path: str):
    if output_path.endswith(".json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(items)} items to {output_path}")
    else:
        # default to CSV
        if not items:
            print("No items to write.")
            return
        # unify keys
        keys = set()
        for it in items:
            keys.update(it.keys())
        keys = list(keys)
        with open(output_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for it in items:
                writer.writerow({k: it.get(k, "") for k in keys})
        print(f"Wrote {len(items)} items to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Site Searcher - extract elements from webpages and save to file")
    parser.add_argument("--url", required=True, help="Target page URL")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--selector", help="CSS selector to extract (e.g. 'a.article')")
    group.add_argument("--xpath", help="XPath expression to extract")
    parser.add_argument("--attr", help="Attribute to extract (e.g. href, src, data-id). If omitted and not --text, returns tag/html.")
    parser.add_argument("--text", action="store_true", help="Also extract element text content")
    parser.add_argument("--headless", action="store_true", help="Use headless browser (Selenium) to render JS before extracting.")
    parser.add_argument("--output", default="results.csv", help="Output filename (.csv or .json)")
    parser.add_argument("--timeout", type=int, default=20, help="Page load timeout seconds")
    args = parser.parse_args()

    url = args.url
    try:
        if args.headless:
            html = fetch_with_selenium(url, timeout=args.timeout, headless=True)
        else:
            html = fetch_static(url, timeout=args.timeout)
    except Exception as e:
        print("Failed to fetch page:", e, file=sys.stderr)
        sys.exit(2)

    items = []
    try:
        if args.selector:
            items = parse_with_selector(html, args.selector, base_url=url, attr=args.attr, text=args.text)
        else:
            items = parse_with_xpath(html, args.xpath, base_url=url, attr=args.attr, text=args.text)
    except Exception as e:
        print("Failed to parse page:", e, file=sys.stderr)
        sys.exit(3)

    save_output(items, args.output)


if __name__ == "__main__":
    main()
