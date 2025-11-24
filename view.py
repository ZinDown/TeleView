import asyncio
import httpx
import re

# ---------------------------------------
# SETTINGS (config.ini မလိုတော့ဘူး)
# ---------------------------------------
PROXY_SOURCE_URL = "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"
WORKERS = 50
TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)

# ---------------------------------------
# LOGO
# ---------------------------------------
def print_logo():
    print(
f"""
========================================
  𝐓ʜɪ𝐬 𝐒ᴄʀɪᴘᴛ 𝐈𝐬 𝐎ᴡɴᴇᴅ 𝐁ʏ Edwin Moses
  [+] Developer -> Mr.Lynn!
  [+] Telegram Username -> @V_VIP_Official
========================================
"""
    )

# ---------------------------------------
# Helpers
# ---------------------------------------
def convert_proxy(proxy: str, proxy_type="http"):
    return {
        "http://": f"{proxy_type}://{proxy}",
        "https://": f"{proxy_type}://{proxy}"
    }

async def fetch(url: str, proxy=None, proxy_type="http"):
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            proxies=convert_proxy(proxy, proxy_type) if proxy else None
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.text
    except:
        return None

def extract_views(html: str):
    if not html:
        return None

    m = re.search(r'tgme_widget_message_views[^>]*>([\d,\.KkMm]+)<', html)
    if not m:
        return None

    val = m.group(1).replace(",", "")
    try:
        if val[-1].lower() == "k":
            return int(float(val[:-1]) * 1_000)
        elif val[-1].lower() == "m":
            return int(float(val[:-1]) * 1_000_000)
        return int(val)
    except:
        return None

# ---------------------------------------
# Proxy Downloader
# ---------------------------------------
async def download_proxies(proxy_type="http"):
    url = PROXY_SOURCE_URL.replace("proxytype=http", f"proxytype={proxy_type}")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url)
            r.raise_for_status()
            proxies = [p.strip() for p in r.text.splitlines() if ":" in p]
            return proxies
    except:
        return []

# ---------------------------------------
# Main Program
# ---------------------------------------
async def main():
    print_logo()

    post_url = input("Enter your Telegram Post URL: ").strip()
    proxy_type = "http"  # (Can change to socks4 / socks5)

    print("\nDownloading proxy list...")
    proxies = await download_proxies(proxy_type)
    print(f"Total proxies fetched: {len(proxies)}")

    print("\nFetching original Telegram post info...")
    html = await fetch(post_url)
    original = extract_views(html)

    print(f"Original Views: {original if original else 'Unknown'}")

    print("\nChecking proxy health...\n")
    ok = 0
    failed = 0

    for proxy in proxies[:WORKERS]:
        result = await fetch(post_url, proxy, proxy_type)
        if result:
            ok += 1
            print(f"[OK] {proxy}")
        else:
            failed += 1
            print(f"[FAIL] {proxy}")

    print("\n========= RESULT SUMMARY =========")
    print(f"Working Proxies: {ok}")
    print(f"Failed Proxies : {failed}")
    print("=================================")

if __name__ == "__main__":
    asyncio.run(main())
