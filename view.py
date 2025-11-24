""" Safe, 2025-style "view.py" — does NOT send fake views.

What this script does (allowed):

Reads proxy list URL from config.ini

Downloads proxies (supports http, socks4, socks5 via --proxy-type)

Tests proxies concurrently (checks if they can fetch the Telegram post page)

Fetches the original (live) view count from the public Telegram post page

Prints a green, bold "logo" line with Script Owner (GitHub / Telegram names)

Reports counts: original views, working proxies, failed proxies


Why this is safe: the script does NOT call Telegram's /v/ endpoint or attempt to increment view counters. It only fetches public page data and validates proxies.

Usage (example): python view.py "https://t.me/example_channel/123" 
--owner "Your Name" --github "your_github" --proxy-type socks5 
--workers 50 --limit 500

"""

import re import asyncio import argparse import configparser from typing import List, Tuple, Optional

import httpx

-------------------------

ANSI styles for terminal

-------------------------

BOLD = "\033[1m" GREEN = "\033[32m" RESET = "\033[0m"

-------------------------

Config defaults

-------------------------

CONFIG_PATH = "config.ini" DEFAULT_PROXY_SECTION = "proxy" DEFAULT_PROXY_KEY = "url"

USER_AGENT = ( "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/131.0 Safari/537.36" ) TELEGRAM_BASE = "https://t.me"

-------------------------

Helpers

-------------------------

def format_proxy_for_httpx(proxy: str, proxy_type: str) -> dict: """Return a proxies mapping for httpx requests. proxy is "ip:port".

httpx supports proxies like "http://host:port" or "socks5://host:port".
"""
scheme = proxy_type.lower()
if scheme not in ("http", "socks4", "socks5"):
    scheme = "http"
return {
    "http://": f"{scheme}://{proxy}",
    "https://": f"{scheme}://{proxy}",
}

async def fetch_text(client: httpx.AsyncClient, url: str, **kwargs) -> Optional[str]: try: r = await client.get(url, **kwargs) r.raise_for_status() return r.text except Exception: return None

def extract_views_from_html(html: str) -> Optional[int]: """Try multiple heuristics to extract the view count from Telegram post HTML.""" if not html: return None

# 1) tgme_widget_message_views span like: <span class="tgme_widget_message_views">1,234</span>
m = re.search(r"tgme_widget_message_views[^>]*>([\d,\.KkMmb]+)<", html)
if m:
    raw = m.group(1)
    return parse_human_number(raw)

# 2) data-view attribute (token) is not a view count, but sometimes original count present elsewhere
m2 = re.search(r"data-view=\"(\d+)\"", html)
if m2:
    try:
        return int(m2.group(1))
    except ValueError:
        pass

# 3) Fallback: search for "views" label with a preceding number
m3 = re.search(r"([\d,\.KkMmb]+)\s*views", html, flags=re.IGNORECASE)
if m3:
    return parse_human_number(m3.group(1))

return None

def parse_human_number(s: str) -> Optional[int]: """Parse numbers like '1,234', '1.2K', '3.4M' into integers. Returns None on failure.""" s = s.strip() try: # plain integer with commas if re.match(r"^[\d,]+$", s): return int(s.replace(",", "")) # 1.2K, 3M, etc. m = re.match(r"^([\d.]+)\s*([KkMmBb])$", s) if m: val = float(m.group(1)) mul = m.group(2).lower() if mul == "k": return int(val * 1_000) if mul == "m": return int(val * 1_000_000) if mul == "b": return int(val * 1_000_000_000) except Exception: return None return None

-------------------------

Core logic

-------------------------

async def download_proxies_list(proxies_url: str, proxy_type: str) -> List[str]: """Download proxies from the provided URL. If the URL contains proxytype=, replace it.

Returns list of proxies as 'ip:port'. Empty list on failure.
"""
try:
    # Try to replace or append proxytype param
    if "proxytype=" in proxies_url:
        url = re.sub(r"proxytype=[^&]+", f"proxytype={proxy_type}", proxies_url)
    else:
        sep = "&" if "?" in proxies_url else "?"
        url = f"{proxies_url}{sep}proxytype={proxy_type}"

    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": USER_AGENT}) as client:
        r = await client.get(url)
        r.raise_for_status()
        lines = [l.strip() for l in r.text.splitlines() if l.strip()]
        # proxyscrape sometimes returns comments or pages; keep only ip:port-looking lines
        proxies = [ln for ln in lines if re.match(r"^\d+\.\d+\.\d+\.\d+:\d+$", ln)]
        return proxies
except Exception:
    return []

async def test_proxy(proxy: str, proxy_type: str, target_url: str, timeout: int = 12) -> Tuple[str, bool, Optional[int]]: """Test a single proxy: whether it can fetch the target_url. Returns (proxy, ok, views_or_none) views_or_none is extracted view count only if the fetch succeeded and the response contained it. """ proxies = format_proxy_for_httpx(proxy, proxy_type) async with httpx.AsyncClient(proxies=proxies, timeout=timeout, headers={"User-Agent": USER_AGENT}) as client: text = await fetch_text(client, target_url, follow_redirects=True) if text is None: return proxy, False, None views = extract_views_from_html(text) return proxy, True, views

async def run_worker_pool(proxies: List[str], proxy_type: str, target_url: str, workers: int = 50) -> Tuple[int, int, List[str], List[str]]: """Test proxies concurrently. Returns (success_count, fail_count, working_proxies, failed_proxies) """ sem = asyncio.Semaphore(workers)

async def _wrapped(p):
    async with sem:
        return await test_proxy(p, proxy_type, target_url)

tasks = [asyncio.create_task(_wrapped(p)) for p in proxies]
results = await asyncio.gather(*tasks)

working = [p for p, ok, v in results if ok]
failed = [p for p, ok, v in results if not ok]
return len(working), len(failed), working, failed

-------------------------

CLI / entrypoint

-------------------------

def print_logo(): B="[1m"; G="[32m"; E="[0m" logo=(f'''{B}{E}========================================{E}

{G}𝐓ʜɪ𝐬 𝐒ᴄʀɪᴘᴛ 𝐈𝐬 𝐎ᴡɴᴇᴅ 𝐁ʏ Edwin Moses{B}

{G}[+] 𝐃ᴇᴠᴇʟᴏᴘᴇʀ -> {B}Mr.Lynn!

{G}[+] 𝐓ᴇʟᴇɢʀᴀᴍ 𝐔sᴇʀɴᴀᴍᴇ -> {B}@V_VIP_Official

{E}==================================================''') print(logo)

async def main(): # Prompt URL input first print_logo() user_url = input(" Enter your Post URL: ")

parser = argparse.ArgumentParser(description="Safe Telegram inspector + proxy tester (does NOT send fake views)")
parser.add_argument("url", default=user_url help="Telegram post URL, e.g. https://t.me/channel/123")
parser.add_argument("--owner", default="Unknown", help="Script owner friendly name")
parser.add_argument("--github", default="unknown", help="Github account name")
parser.add_argument("--proxy-type", default="http", choices=["http", "socks4", "socks5"], help="Proxy type to request from proxyscrape")
parser.add_argument("--workers", type=int, default=50, help="Concurrent proxy tester workers")
parser.add_argument("--limit", type=int, default=500, help="Max number of proxies to test (trim list)")
parser.add_argument("--config", default=CONFIG_PATH, help="Path to config.ini")

args = parser.parse_args()

print_logo(args.owner, args.github)

# Load config
cfg = configparser.ConfigParser()
cfg.read(args.config)
proxies_url = cfg.get(DEFAULT_PROXY_SECTION, DEFAULT_PROXY_KEY, fallback=None)
if not proxies_url:
    print(f"{BOLD}Error:{RESET} proxy URL not found in {args.config} under [{DEFAULT_PROXY_SECTION}] {DEFAULT_PROXY_KEY}")
    return

print(f"{BOLD}Downloading proxy list...{RESET}")
proxies = await download_proxies_list(proxies_url, args.proxy_type)
if not proxies:
    print(f"{BOLD}Warning:{RESET} failed to download any proxies from {proxies_url}")
    return

print(f"Total proxies downloaded: {len(proxies)}")
proxies = proxies[: args.limit]
print(f"Testing up to {len(proxies)} proxies with {args.workers} workers (type={args.proxy_type})...")

# Test proxies
success_count, fail_count, working, failed = await run_worker_pool(proxies, args.proxy_type, args.url, workers=args.workers)

# Try to fetch original view count without proxy (single request)
original_views = None
async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as client:
    html = await fetch_text(client, args.url, follow_redirects=True)
    original_views = extract_views_from_html(html)

print("\n" + "=" * 40)
print(f"{BOLD}RESULTS{RESET}")
print(f"Original (live) views: {BOLD}{original_views if original_views is not None else 'Unknown'}{RESET}")
print(f"Working proxies: {BOLD}{success_count}{RESET}")
print(f"Failed proxies: {BOLD}{fail_count}{RESET}")
print("\nTop 10 working proxies:")
for p in working[:10]:
    print(f" - {p}")

print("\nDone.")

if name == "main": try: asyncio.run(main()) except KeyboardInterrupt: print("Interrupted by user. Exiting.")

