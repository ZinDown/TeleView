import requests
import socket
from urllib.parse import urlparse
import socks
import time

# ProxyScrape API URL (HTTP proxies)
PROXY_URL = "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"

# Timeout seconds
TIMEOUT = 10

# Fetch proxy list
def fetch_proxies():
    try:
        response = requests.get(PROXY_URL, timeout=TIMEOUT)
        response.raise_for_status()
        proxies = [p.strip() for p in response.text.split("\n") if p.strip()]
        print(f"Fetched {len(proxies)} proxies")
        return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
        return []

# Test Proxy (HTTP only)
def test_proxy(proxy_str, test_url):
    try:
        host, port = proxy_str.split(":")
        proxies = {
            "http": f"http://{host}:{port}",
            "https": f"http://{host}:{port}"
        }

        r = requests.get(test_url, proxies=proxies, timeout=TIMEOUT)
        if r.status_code == 200:
            return proxy_str, True
    except:
        return proxy_str, False

    return proxy_str, False

# Main program
if __name__ == "__main__":
    test_url = input("Enter the test URL (include http:// or https://): ").strip()

    if not test_url.startswith("http"):
        print("Invalid URL. Must start with http:// or https://")
        exit()

    proxies = fetch_proxies()
    working = []

    for proxy in proxies:
        proxy_ip, is_working = test_proxy(proxy, test_url)
        status = "WORKING" if is_working else "FAIL"
        print(f"{proxy_ip} → {status}")

        if is_working:
            working.append(proxy_ip)

        time.sleep(0.5)

    print("\n=== Working Proxies ===")
    for p in working:
        print(p)
