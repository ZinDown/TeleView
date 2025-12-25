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
BASE_URL = "https://maynoe.com/page/"  
PROXY = "https://api.codetabs.com/v1/proxy?quest="  
  
HEADERS = {  
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",  
    "Accept-Language": "en-US,en;q=0.9",  
    "Accept": "text/html"  
}  
  
OUTPUT_DIR = "/storage/emulated/0"  
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "MayNoe.json")  
  
def clear():  
    os.system("cls" if os.name == "nt" else "clear")  
  
# ================= BANNER =================  
def banner():  
    clear()  
    text = pyfiglet.figlet_format("MAYNOE", font="slant")  
    print(Fore.GREEN + text)  
    print(Fore.YELLOW + "Maynoe Scraper ( 𝐒𝐜𝐫𝐢𝐩𝐭 𝐁𝐲 𝐋𝐲𝐧𝐧 )")  
    print(Fore.CYAN + "-" * 40)  
  
    print()  
  
# ================= SCRAPER =================  
def scrape_page(page):  
    url = f"{BASE_URL}{page}/"  
    proxy_url = PROXY + url  
  
    try:  
        r = requests.get(proxy_url, headers=HEADERS, timeout=25)  
  
        # ✅ Myanmar Unicode FIX  
        html = r.content.decode("utf-8", errors="ignore")  
        soup = BeautifulSoup(html, "html.parser")  
  
        items = soup.select(".clean-grid-grid-post-thumbnail")  
        results = []  
  
        for item in items:
            link_elem = item.select_one("a")
            img_elem = item.select_one("img")
            if not link_elem or not img_elem:
                continue

            title = link_elem.get("title", "").replace("Permanent Link to ", "").strip()
            href = link_elem.get("href", "")
            image = img_elem.get("src", "")

            link = f"https://zindown.github.io/maynoeplayer.html?url={href}"

            results.append({
                "title": title,
                "image": image,
                "link": link,
                "type": "web"
            })
        return results
  
    except Exception as e:  
        print(Fore.RED + f"[ERROR] Page {page} failed → {e}")  
        return []  
  
# ================= MAIN =================  
def main():  
    banner()  
  
    try:  
        start = int(input(Fore.CYAN + "Start Page : "))  
        end   = int(input(Fore.CYAN + "End Page   : "))  
    except:  
        print(Fore.RED + "Invalid page number!")  
        sys.exit(1)  
  
    all_data = []  
  
    print()  
    for p in range(start, end + 1):  
        print(  
            Fore.YELLOW +  
            f"[+] Scraping page {p} of {end} ..."  
        )  
        page_data = scrape_page(p)  
        all_data.extend(page_data)  
        time.sleep(1)  
  
    result = {  
        "apyar": all_data  
    }  
  
    # ================= SAVE JSON ONLY =================  
    try:  
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:  
            json.dump(result, f, indent=2, ensure_ascii=False)  
  
        print()  
        print(Fore.GREEN + "✔ Scraping finished successfully!")  
        print(Fore.GREEN + f"✔ JSON saved to storage as: {OUTPUT_FILE}")  
        #print(Fore.CYAN + "✔ 𝗦𝗰𝗿𝗶𝗽𝘁 𝗕𝘆 𝗟𝘆𝗻𝗻 ")  
  
    except Exception as e:  
        print(Fore.RED + f"Failed to save JSON → {e}")  
  
# ================= RUN =================  
if __name__ == "__main__":  
    main()  
  
