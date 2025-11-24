import requests
import socket
from requests.exceptions import RequestException
from urllib.parse import urlparse
import socks
import time

# ProxyScrape API URL
PROXY_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"

# Test URLs (HTTP & HTTPS)
TEST_URLS = {
    "HTTP": "http://example.com",
    "HTTPS": "https://www.google.com"
}

# Timeout in seconds
TIMEOUT = 10

# Fetch proxy list
def fetch_proxies():
    try:
        response = requests.get(PROXY_URL, timeout=10)
        response.raise_for_status()
        proxies = [p.strip() for p in response.text.split("\n") if p.strip()]
        print(f"Fetched {len(proxies)} proxies")
        return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
        return []

# Test single proxy
def test_proxy(proxy_str):
    protocol = "HTTP"
    proxy_raw = proxy_str

    if proxy_str.startswith("socks4://"):
        protocol = "SOCKS4"
        proxy_raw = proxy_str.replace("socks4://", "")
    elif proxy_str.startswith("socks5://"):
        protocol = "SOCKS5"
        proxy_raw = proxy_str.replace("socks5://", "")
    elif proxy_str.startswith("http://"):
        protocol = "HTTP"
        proxy_raw = proxy_str.replace("http://", "")

    parts = proxy_raw.split(":")
    if len(parts) < 2:
        return proxy_str, protocol, False

    host = parts[0]
    port = int(parts[1])

    try:
        if protocol in ["HTTP", "HTTPS"]:
            proxies = {
                "http": f"http://{host}:{port}",
                "https": f"http://{host}:{port}"
            }
            r = requests.get(TEST_URLS["HTTP"], proxies=proxies, timeout=TIMEOUT)
            if r.status_code == 200:
                return proxy_str, protocol, True
        else:  # SOCKS4/5
            s = socks.socksocket()
            if protocol == "SOCKS4":
                s.set_proxy(socks.SOCKS4, host, port)
            else:
                s.set_proxy(socks.SOCKS5, host, port)
            s.settimeout(TIMEOUT)
            url = urlparse(TEST_URLS["HTTP"])
            s.connect((url.hostname, url.port or 80))
            return proxy_str, protocol, True
    except Exception:
        return proxy_str, protocol, False

# Main
if __name__ == "__main__":
    proxies = fetch_proxies()
    working = []

    for proxy in proxies:
        proxy_str, protocol, is_working = test_proxy(proxy)
        status = "WORKING" if is_working else "FAIL"
        print(f"{proxy_str} ({protocol}) → {status}")
        if is_working:
            working.append(proxy_str)
        time.sleep(0.5)  # small delay to avoid rapid requests

    print("\n=== Working Proxies ===")
    for p in working:
        print(p)
