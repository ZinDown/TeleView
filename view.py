import asyncio
import httpx
import re

PROXY_SOURCE_URL = "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"
TIMEOUT = 10
WORKERS = 50

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}


async def fetch(url, proxy=None):
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT,
            headers=HEADERS,
            proxies=proxy
        ) as client:
            r = await client.get(url)
            return r.text
    except:
        return None


async def download_proxies():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(PROXY_SOURCE_URL)
        return [p.strip() for p in r.text.splitlines() if ":" in p]


def build_proxy(proxy, ptype="http"):
    return f"{ptype}://{proxy}"


async def main():
    print("\nDownloading proxies...\n")
    proxies = await download_proxies()

    print(f"Total proxies: {len(proxies)}\n")

    test_url = "https://httpbin.org/ip"
    working = 0
    failed = 0

    for p in proxies[:WORKERS]:
        proxy_url = build_proxy(p)
        text = await fetch(test_url, proxy=proxy_url)
        if text:
            working += 1
            print(f"[OK] {p}")
        else:
            failed += 1
            print(f"[FAIL] {p}")

    print("\n============ RESULT ============")
    print(f"Working Proxies: {working}")
    print(f"Failed Proxies : {failed}")
    print("=================================\n")


if __name__ == "__main__":
    asyncio.run(main())
