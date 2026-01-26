import requests
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import pyfiglet
from colorama import Fore, Style, init

init(autoreset=True)

# ================= CONFIG =================
PROXY = "https://api.codetabs.com/v1/proxy?quest="
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html"
}

# ================= PATH AUTO DETECT =================
def get_output_dir():
    if "ANDROID_ROOT" in os.environ:
        return "/storage/emulated/0"

    base = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base, "output")
    os.makedirs(out, exist_ok=True)
    return out

# ================= UTILS =================
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear()
    text = pyfiglet.figlet_format("LYNN XU", font="slant")
    print(Fore.GREEN + text)
    print(Fore.YELLOW + "Multi Scraper Tool")
    print(Fore.CYAN + "Script By Lynn")
    print(Fore.CYAN + "-" * 45)
    print()


def wait_and_return():
    print()
    input(Fore.CYAN + "Press ENTER to return main menu...")
    main_menu()

# ================= MENU =================
def main_menu():
    banner()
    print(Fore.GREEN + Style.BRIGHT + "[ 1 ] MMPORNS.com")
    print(Fore.GREEN + Style.BRIGHT + "[ 2 ] SAMUSAR.com")
    print(Fore.RED   + Style.BRIGHT + "[ 0 ] Exit")
    print()

    choice = input(Fore.YELLOW + "Select Option (0 / 1 / 2): ").strip()

    if choice == "1":
        run_mmporns()
    elif choice == "2":
        run_samusar()
    elif choice == "0":
        print(Fore.GREEN + "Bye Bye 👋")
        sys.exit(0)
    else:
        print(Fore.RED + "Invalid choice!")
        time.sleep(1)
        main_menu()

# ================= MMPORNS =================
def scrape_mmporns(page):
    url = f"https://mmporns.com/page/{page}/?filter=latest"
    proxy_url = PROXY + url

    try:
        r = requests.get(proxy_url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.content.decode("utf-8", "ignore"), "html.parser")

        items = soup.find_all("article")
        results = []

        for item in items:
            title_el = item.find("h2")
            title = title_el.get_text(strip=True) if title_el else "No Title"

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
        print(Fore.RED + f"[ERROR] {e}")
        return []

def run_mmporns():
    banner()
    print(Fore.GREEN + Style.BRIGHT + "MMPORNS.com Scraper")
    print(Fore.CYAN + "-" * 45)

    try:
        start = int(input(Fore.CYAN + "Start Page : "))
        end   = int(input(Fore.CYAN + "End Page   : "))
    except:
        print(Fore.RED + "Invalid page number!")
        time.sleep(1)
        main_menu()

    all_data = []

    for p in range(start, end + 1):
        print(Fore.YELLOW + f"[+] Scraping page {p} ...")
        data = scrape_mmporns(p)

        count = len(data)
        print(
            "    " +
            (Fore.CYAN if count > 0 else Fore.RED) +
            Style.BRIGHT +
            f"➜ Items found : {count}"
        )

        all_data.extend(data)
        time.sleep(1)

    OUTPUT_DIR = get_output_dir()
    output = os.path.join(OUTPUT_DIR, "MMPorns.json")

    with open(output, "w", encoding="utf-8") as f:
        json.dump({"apyar": all_data}, f, indent=2, ensure_ascii=False)

    print()
    print(Fore.GREEN + Style.BRIGHT + "✔ Scraping finished successfully!")
    print(Fore.GREEN + Style.BRIGHT + f"✔ Total Items : {len(all_data)}")
    print(Fore.GREEN + f"✔ File saved  : {output}")
    wait_and_return()

# ================= SAMUSAR =================
def scrape_samusar(page):
    url = f"https://www.samusar.com/latest-updates/{page}/"
    proxy_url = PROXY + url

    try:
        r = requests.get(proxy_url, headers=HEADERS, timeout=25)
        soup = BeautifulSoup(r.content.decode("utf-8", "ignore"), "html.parser")

        items = soup.select(".item > a[title]")
        results = []

        for item in items:
            title = item.get("title", "").strip()
            href = item.get("href", "")

            video_id = ""
            if "/videos/" in href:
                try:
                    video_id = href.split("/videos/")[1].split("/")[0]
                except:
                    pass

            img = item.select_one(".img img")
            image = img["src"] if img and img.has_attr("src") else ""

            link = (
                "https://zindown.github.io/samusarplayer.html"
                f"?url=https://www.samusar.com/embed/{video_id}"
            )

            results.append({
                "title": title,
                "image": image,
                "link": link,
                "type": "web"
            })

        return results

    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}")
        return []

def run_samusar():
    banner()
    print(Fore.GREEN + Style.BRIGHT + "SAMUSAR.com Scraper")
    print(Fore.CYAN + "-" * 45)

    try:
        start = int(input(Fore.CYAN + "Start Page : "))
        end   = int(input(Fore.CYAN + "End Page   : "))
    except:
        print(Fore.RED + "Invalid page number!")
        time.sleep(1)
        main_menu()

    all_data = []

    for p in range(start, end + 1):
        print(Fore.YELLOW + f"[+] Scraping page {p} ...")
        data = scrape_samusar(p)

        count = len(data)
        print(
            "    " +
            (Fore.CYAN if count > 0 else Fore.RED) +
            Style.BRIGHT +
            f"➜ Items found : {count}"
        )

        all_data.extend(data)
        time.sleep(1)

    OUTPUT_DIR = get_output_dir()
    output = os.path.join(OUTPUT_DIR, "SaMuSar.json")

    with open(output, "w", encoding="utf-8") as f:
        json.dump({"apyar": all_data}, f, indent=2, ensure_ascii=False)

    print()
    print(Fore.GREEN + Style.BRIGHT + "✔ Scraping finished successfully!")
    print(Fore.GREEN + Style.BRIGHT + f"✔ Total Items : {len(all_data)}")
    print(Fore.GREEN + f"✔ File saved  : {output}")
    wait_and_return()

# ================= RUN =================
if __name__ == "__main__":
    main_menu()
