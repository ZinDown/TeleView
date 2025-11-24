import requests
import socket
from urllib.parse import urlparse
import socks
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ProxyScrape API URL
PROXY_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"

# Timeout in seconds
TIMEOUT = 10
MAX_THREADS = 50   # <-- Change this to speed up/slow down

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

# Test a single proxy
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

    host = parts[0]
    port = int(parts[1])

    try:
        if protocol == "HTTP":
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


# MAIN (multi-threaded)
if __name__ == "__main__":
    test_url = input("Enter URL to test (e.g., https://google.com): ").strip()
    if not test_url.startswith("http"):
        test_url = "http://" + test_url

    proxies = fetch_proxies()
    working = []

    print("\nTesting proxies with threads...\n")

    # Use ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_tasks = {
            executor.submit(test_proxy, proxy, test_url): proxy for proxy in proxies
        }

        for future in as_completed(future_tasks):
            proxy = future_tasks[future]
            try:
                proxy_str, protocol, ok = future.result()
                status = "WORKING" if ok else "FAIL"
                print(f"{proxy_str} ({protocol}) → {status}")
                if ok:
                    working.append(proxy_str)
            except Exception:
                print(f"{proxy} → ERROR")

    print("\n=== Working Proxies ===")
    for p in working:
        print(p)

    print(f"\nTotal Working: {len(working)}")
