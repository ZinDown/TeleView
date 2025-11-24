import asyncio
import httpx
import configparser
from typing import List, Optional
import re

# ----------------------------
# Load config
# ----------------------------
config = configparser.ConfigParser()
config.read("config.ini")

PROXY_URL = config.get("proxy", "url")
WORKERS = config.getint("settings", "workers")
TIMEOUT = config.getint("settings", "timeout")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

# ----------------------------
# Helpers
# ----------------------------
def format_proxy(proxy: str, proxy_type: str) -> dict:
    scheme = proxy_type.lower()
    return {"http://": f"{scheme}://{proxy}", "https://": f"{scheme}://{proxy}"}

async def fetch_text(url: str, proxy: Optional[str]=None, proxy_type: str="http") -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, proxies=format_proxy(proxy, proxy_type) if proxy else None) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception:
        return None

def extract_views(html: str) -> Optional[int]:
    """Extract Telegram public view count safely."""
    if not html:
        return None
    m = re.search(r"tgme_widget_message_views[^>]*>([\d,\.KkMm]+)<", html)
    if m:
        val = m.group(1).replace(",", "")
        try:
            if val[-1].lower() == "k":
                return int(float(val[:-1])*1_000)
            if val[-1].lower() == "m":
                return int(float(val[:-1])*1_000_000)
            return int(val)
        except:
            return None
    return None

# ----------------------------
# Proxy downloader
# ----------------------------
async def download_proxies(proxy_type: str="http") -> List[str]:
    url = PROXY_URL
    if "proxytype=" in url:
        url = re.sub(r"proxytype=[^&]+", f"proxytype={proxy_type}", url)
    else:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}proxytype={proxy_type}"

    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": USER_AGENT}) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            proxies = [p.strip() for p in r.text.splitlines() if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", p)]
            return proxies
        except:
            return []

# ----------------------------
# Main Async
# ----------------------------
async def main():
    print("=== 𝐓ʜɪ𝐬 𝐒ᴄʀɪᴘᴛ 𝐈𝐬 𝐎ᴡɴᴇᴅ 𝐁ʏ Edwin Moses ===")
    print("[+] Developer: Mr.Lynn")
    print("[+] Telegram: @V_VIP_Official")
    print("="*50)

    post_url = input("Enter your Telegram Post URL: ").strip()
    proxy_type = "http"  # can be socks4/socks5

    proxies = await download_proxies(proxy_type)
    print(f"Total proxies downloaded: {len(proxies)}")

    html = await fetch_text(post_url)
    views = extract_views(html)
    print(f"Original Views: {views if views is not None else 'Unknown'}")

    # Proxy check simulation (without sending fake views)
    ok_count = 0
    for proxy in proxies[:WORKERS]:
        if await fetch_text(post_url, proxy, proxy_type):
            ok_count += 1
    print(f"Working Proxies: {ok_count}")
    print(f"Failed Proxies: {len(proxies)-ok_count}")

if __name__ == "__main__":
    asyncio.run(main())
