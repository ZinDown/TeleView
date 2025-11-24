import requests
import socks
import socket
import ssl
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Proxy List Source (free proxies) ---
PROXY_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"

# Timeout and threads
TIMEOUT = 10
MAX_THREADS = 100

# --- Fetch free proxies ---
def fetch_proxies():
    try:
        r = requests.get(PROXY_URL, timeout=10)
        r.raise_for_status()
        proxies = [p.strip() for p in r.text.split("\n") if p.strip()]
        print(f"Fetched {len(proxies)} proxies")
        return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
        return []

# --- Test single proxy ---
def test_proxy(proxy_str, test_url):
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

    host, port = parts[0], int(parts[1])

    try:
        if protocol == "HTTP":
            # HTTPS support using CONNECT
            proxies = {
                "http": f"http://{host}:{port}",
                "https": f"http://{host}:{port}",
            }
            r = requests.get(test_url, proxies=proxies, timeout=TIMEOUT)
            if r.status_code == 200:
                return proxy_str, protocol, True

        else:  # SOCKS4/5
            s = socks.socksocket()
            if protocol == "SOCKS4":
                s.set_proxy(socks.SOCKS4, host, port)
            else:
                s.set_proxy(socks.SOCKS5, host, port)
            s.settimeout(TIMEOUT)

            url = urlparse(test_url)
            dest_port = url.port or (443 if url.scheme == "https" else 80)
            s.connect((url.hostname, dest_port))

            if url.scheme == "https":
                s = ssl.create_default_context().wrap_socket(s, server_hostname=url.hostname)

            return proxy_str, protocol, True

    except Exception:
        return proxy_str, protocol, False

# --- Simulated Telegram view request (educational) ---
def simulate_telegram_view(proxy_str):
    """
    Educational only.
    Demonstrates how Telegram checks IP without counting real views.
    """
    try:
        host, port = proxy_str.split(":")
        # Telegram ignores most free proxies
        print(f"[Telegram Test] Proxy {host}:{port} likely blocked (educational)")
        return False
    except Exception:
        return False

# --- Main ---
if __name__ == "__main__":
    test_url = input("Enter a test URL (https://example.com): ").strip()
    if not test_url.startswith("http"):
        test_url = "http://" + test_url

    proxies = fetch_proxies()
    working = []

    print("\n--- Testing proxies in parallel ---\n")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(test_proxy, proxy, test_url): proxy for proxy in proxies}
        for future in as_completed(futures):
            proxy, protocol, ok = future.result()
            status = "WORKING" if ok else "FAIL"
            print(f"{proxy} ({protocol}) → {status}")
            if ok:
                working.append(proxy)

    print("\n=== Working Proxies ===")
    for p in working:
        print(p)

    print("\n--- Simulated Telegram View Check ---\n")
    for proxy in working:
        simulate_telegram_view(proxy)

    print("\nDone. (Telegram view simulation only, not real boosting)")
