import requests
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import pyfiglet
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "https://mmporns.com/page/"
PROXY = "https://api.codetabs.com/v1/proxy?quest="
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUTPUT_FILE = "/storage/emulated/0/MMPorns_Data.json"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def scrape_page(page):
    url = f"{BASE_URL}{page}/?filter=latest"
    proxy_url = PROXY + url

    try:
        r = requests.get(proxy_url, headers=HEADERS, timeout=30)
        html = r.content.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")

        items = soup.find_all("article")
        results = []

        for item in items:
            title_el = item.find("h2")
            if title_el:
                title = title_el.get_text(strip=True)
            else:
                img_el = item.find("img")
                title = img_el.get("alt", "No Title Found").strip() if img_el else "No Title"

            img_el = item.find("img")
            image = img_el.get("src", "") if img_el else ""

            link_el = item.find("a")
            link = link_el.get("href", "") if link_el else ""
            if link and not link.startswith("http"):
                link = "https://mmporns.com" + link

            results.append({
                "title": title,
                "image": image,
                "link": link,
                "type": "web"
            })

        return results

    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        return []


def main():
    clear_screen()  

    text = pyfiglet.figlet_format("MMPORNS", font="slant")
    print(Fore.GREEN + text)
    print(Fore.YELLOW + "MMPorns Scraper ( 𝐒𝐜𝐫𝐢𝐩𝐭 𝐁𝐲 𝐋𝐲𝐧𝐧 )")
    print(Fore.CYAN + "-" * 40)

    start = int(input("Start Page: "))
    end = int(input("End Page: "))

    final_data = []

    for p in range(start, end + 1):
        print(Fore.YELLOW + f"Scraping Page {p} from mmporns.com...")
        data = scrape_page(p)
        final_data.extend(data)
        print(Fore.CYAN + f"Found {len(data)} items")
        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"apyar": final_data}, f, indent=2, ensure_ascii=False)

    print(Fore.GREEN + "✔ Scraping finished successfully!")
    print(Fore.GREEN + f"\nSuccess! Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
