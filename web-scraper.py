#!/usr/bin/env python3
"""
web-scraper.py — Lightweight web scraping framework

Beautiful terminal output, easy configuration, export to multiple formats.
Pure Python 3.7+, zero dependencies.

Usage:
    python web-scraper.py <url> --element <css_selector>
    python web-scraper.py <url> --json
    python web-scraper.py <url> --csv
    python web-scraper.py <url> --headers

Support: https://github.com/yourusername/web-scraper
"""

import sys
import json
import csv
import io
import urllib.request
import html
from urllib.parse import urlparse, urljoin
from xml.etree.ElementTree import fromstring
import re


def fetch_page(url, headers=None):
    """Fetch webpage content"""
    if headers is None:
        headers = {"User-Agent": "web-scraper/1.0"}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return {"error": str(e)}


def simple_css_selector(html_content, selector):
    """Simple CSS selector support (limited but useful)"""
    # This is a very basic implementation - for production, use BeautifulSoup
    # Supports: tag, class, id, and basic attribute selectors
    
    # Handle class selector
    if selector.startswith('.'):
        class_name = selector[1:]
        pattern = re.compile(rf'<[^>]+class="[^"]*{class_name}[^"]*"[^>]*>(.*?)</[^>]+>', re.DOTALL)
        return [html.unescape(m.group(1).strip()) for m in pattern.finditer(html_content)]
    
    # Handle ID selector
    elif selector.startswith('#'):
        id_name = selector[1:]
        pattern = re.compile(rf'<[^>]+id="{id_name}"[^>]*>(.*?)</[^>]+>', re.DOTALL)
        matches = pattern.search(html_content)
        return [html.unescape(matches.group(1).strip())] if matches else []
    
    # Handle tag selector
    elif not selector.startswith('.') and not selector.startswith('#'):
        pattern = re.compile(rf'<{selector}[^>]*>(.*?)</{selector}>', re.DOTALL)
        return [html.unescape(m.group(1).strip()) for m in pattern.finditer(html_content)]
    
    return []


def extract_links(html_content, base_url=""):
    """Extract all links from page"""
    if base_url:
        base = urlparse(base_url).scheme + "://" + urlparse(base_url).netloc
    
    pattern = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
    links = []
    
    for match in pattern.finditer(html_content):
        href = match.group(1).strip()
        text = html.unescape(match.group(2).strip())
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text and href:
            # Make relative URLs absolute
            if href.startswith('/'):
                href = base + href
            elif not href.startswith(('http', 'mailto:', '#')):
                href = base.rstrip('/') + '/' + href.lstrip('/')
            
            links.append({'text': text, 'url': href})
    
    return links


def extract_emails(html_content):
    """Extract email addresses from page"""
    pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return list(set(pattern.findall(html_content)))


def display_results(url, data, format_type="table"):
    """Display scraped results"""
    if "error" in data:
        print(f"❌ Error: {data['error']}\n")
        return
    
    if format_type == "json":
        print(json.dumps(data, indent=2))
        return
    
    print(f"\n  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║           🕷️  WEB SCRAPER                                   ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"  URL: {url}\n")
    
    if 'links' in data:
        print(f"  Found {len(data['links'])} links:")
        for i, link in enumerate(data['links'][:20], 1):  # Show first 20
            print(f"  [{i:>2}] {link['text']}")
            print(f"      → {link['url']}")
        print()
    
    if 'emails' in data:
        print(f"  Found {len(data['emails'])} emails:")
        for email in data['emails']:
            print(f"  • {email}")
        print()
    
    if 'elements' in data:
        print(f"  Found {len(data['elements'])} elements:")
        for i, elem in enumerate(data['elements'][:20], 1):
            print(f"  [{i:>2}] {elem[:100]}...")
        print()
    
    print(f"  📦 Source: https://github.com/yourusername/web-scraper\n")


def main():
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    # Parse arguments
    url = None
    flags = []
    element_selector = None
    
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            flags.append(args[i][2:])
            if args[i] == '--element' and i + 1 < len(args):
                element_selector = args[i + 1]
                i += 1
        else:
            url = args[i]
        i += 1
    
    if not url:
        print("❌ URL required\n")
        return
    
    content = fetch_page(url)
    if isinstance(content, str):
        data = {}
        
        # Extract all links
        data['links'] = extract_links(content, url)
        
        # Extract emails
        data['emails'] = extract_emails(content)
        
        # Extract specific elements if requested
        if element_selector:
            data['elements'] = simple_css_selector(content, element_selector)
        
        format_type = "json" if "json" in flags else "table"
        display_results(url, data, format_type)
    else:
        print(f"❌ Error: {content}\n")


if __name__ == "__main__":
    main()
