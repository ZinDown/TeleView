import requests
import json
import os
import sys
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyfiglet
from colorama import Fore, Style, init

init(autoreset=True)

# ================= CONFIG =================
PROXY = "https://api.codetabs.com/v1/proxy?quest="
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html"
}

# ================= PATH AUTO DETECT =================
def get_output_dir():
    if "ANDROID_ROOT" in os.environ or os.path.exists("/storage/emulated/0"):
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
    print(Fore.GREEN + Style.BRIGHT + text)
    print(Fore.YELLOW + Style.BRIGHT + "Multi Scraper Tool")
    print(Fore.CYAN + "Script By Lynn")
    print(Fore.MAGENTA + "-" * 45)
    print()

def pause():
    input(Fore.CYAN + "\nPress ENTER to return menu...")
    main_menu()

# ================= MENU =================
def main_menu():
    banner()
    print(Fore.GREEN + "[ 1 ] MMPORNS.com")
    print(Fore.GREEN + "[ 2 ] SAMUSAR.com")
    print(Fore.RED   + "[ 0 ] Exit\n")
    c = input(Fore.YELLOW + "Select : ").strip()
    if c == "1":
        mmporns_menu()
    elif c == "2":
        run_samusar()
    elif c == "0":
        sys.exit()
    else:
        main_menu()

# ================= MMPORNS MENU =================
def mmporns_menu():
    banner()
    print(Fore.CYAN + "-" * 45)
    print(Fore.GREEN + "[ 1 ] Normal Link")
    print(Fore.GREEN + "[ 2 ] MP4 Link (FAST)")
    print(Fore.CYAN + "-" * 45)
    mode = input(Fore.YELLOW + "Select Mode : ").strip()
    if mode not in ("1", "2"):
        return main_menu()
    try:
        start = int(input(Fore.CYAN + "Start Page : "))
        end   = int(input(Fore.CYAN + "End Page   : "))
    except:
        return main_menu()
    run_mmporns(start, end, mode)

# ================= MP4 FAST =================
def get_mp4_fast(url):
    try:
        r = requests.get(PROXY + url, headers=HEADERS, timeout=12)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        meta = soup.find("meta", {"itemprop": "contentURL"})
        return meta["content"] if meta else ""
    except:
        return ""

# ================= MMPORNS =================
def run_mmporns(start, end, mode):
    banner()
    total_items = 0
    total_mp4 = 0
    all_data = []

    for p in range(start, end + 1):
        print(Fore.YELLOW + Style.BRIGHT + f"[+] Scraping Page {p}")
        url = f"https://mmporns.com/page/{p}/?filter=latest"
        r = requests.get(PROXY + url, headers=HEADERS, timeout=25)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all("article")
        temp_rows = []
        video_pages = []

        for item in items:
            title_el = item.find("h2")
            if title_el:
                title = title_el.get_text(strip=True)
            else:
                img_el = item.find("img")
                title = img_el.get("alt", "No Title").strip() if img_el else "No Title"

            img = item.find("img")
            image = img["src"] if img else ""

            a = item.find("a")
            link = a.get("href", "") if a else ""
            if link and not link.startswith("http"):
                link = "https://mmporns.com" + link

            temp_rows.append({
                "title": title,
                "image": image,
                "link": link,
                "type": "x"
            })

            if mode == "2":
                video_pages.append(link)

            total_items += 1

        # ===== MP4 FAST THREAD =====
        mp4_map = {}
        page_mp4 = 0

        if mode == "2" and video_pages:
            print(Fore.CYAN + "    🎬 Scraping MP4 (FAST)...")
            with ThreadPoolExecutor(max_workers=10) as exe:
                tasks = {exe.submit(get_mp4_fast, u): u for u in video_pages}
                idx = 0
                for fut in as_completed(tasks):
                    mp4 = fut.result()
                    if mp4:
                        idx += 1
                        page_mp4 += 1
                        total_mp4 += 1
                        mp4_map[tasks[fut]] = mp4
                        print(Fore.GREEN + Style.BRIGHT + f"        [{idx:02d}] 🎬 Found MP4")

        # ===== APPLY RESULT =====
        for row in temp_rows:
            if mode == "2" and row["link"] in mp4_map:
                row["link"] = mp4_map[row["link"]]
                row["type"] = "direct"
            else:
                row["type"] = "x"
            all_data.append(row)

        print(
            Fore.GREEN +
            f"    ✔ Found Items : {len(temp_rows)}"
            + (Fore.CYAN + f"   🎬 Found MP4 : {page_mp4}" if mode == "2" else "")
        )
        time.sleep(0.3)

    out = os.path.join(get_output_dir(), "MMPorns.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"apyar": all_data}, f, indent=2, ensure_ascii=False)

    print(Fore.MAGENTA + "-" * 45)
    print(Fore.GREEN + Style.BRIGHT + f"✔ Total Items : {total_items}")
    if mode == "2":
        print(Fore.CYAN + Style.BRIGHT + f"🎬 Total MP4   : {total_mp4}")
    print(Fore.GREEN + f"✔ Saved File  : {out}")
    pause()

# ================= SAMUSAR (UNCHANGED) =================
def run_samusar():
    banner()
    try:
        start = int(input(Fore.CYAN + "Start Page : "))
        end   = int(input(Fore.CYAN + "End Page   : "))
    except:
        return main_menu()

    all_data = []
    total = 0

    for p in range(start, end + 1):
        print(Fore.YELLOW + f"[+] Scraping Page {p}")
        url = f"https://www.samusar.com/latest-updates/{p}/"
        r = requests.get(PROXY + url, headers=HEADERS, timeout=20)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select(".item > a[title]")
        count = 0

        for item in items:
            title = item.get("title", "")
            href = item.get("href", "")
            vid = href.split("/videos/")[1].split("/")[0] if "/videos/" in href else ""

            img = item.select_one(".img img")
            image = img["src"] if img else ""

            link = (
           
                f"https://www.samusar.com/embed/{vid}"
            )

            all_data.append({
                "title": title,
                "image": image,
                "link": link,
                "type": "iframe"
            })
            count += 1
            total += 1

        print(Fore.GREEN + f"    ✔ Found Items : {count}")
        time.sleep(0.3)

    out = os.path.join(get_output_dir(), "SaMuSar.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"apyar": all_data}, f, indent=2, ensure_ascii=False)

    print(Fore.MAGENTA + "-" * 45)
    print(Fore.GREEN + f"✔ Total Items : {total}")
    print(Fore.GREEN + f"✔ Saved File  : {out}")
    pause()

# ================= RUN =================
if __name__ == "__main__":
    main_menu()
