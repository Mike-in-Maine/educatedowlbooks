import requests
import time

# =========================
# CONFIG
# =========================

ISBN_LIST = [
    "0068596022",
    "1335009833",
    "0060950196",
    "0385494122",
    "0050014234",
    "0736908552",
]

LOC_SRU = "https://lccn.loc.gov/sru"

HEADERS = {
    "User-Agent": "EducatedOwlBooks/1.0 (LoC BIBFRAME/MODS SRU)"
}

TIMEOUT = 30
SLEEP = 1

# =========================
# SRU QUERY
# =========================

def fetch_loc_mods_by_isbn(isbn: str) -> str:
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": f"bath.isbn={isbn}",
        "recordSchema": "mods",
        "maximumRecords": 1,
    }

    r = requests.get(
        LOC_SRU,
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.text


# =========================
# MAIN
# =========================

def main():
    for isbn in ISBN_LIST:
        print("=" * 100)
        print(f"ISBN: {isbn}")

        try:
            xml = fetch_loc_mods_by_isbn(isbn)
        except Exception as e:
            print(f"ERROR querying LoC SRU: {e}")
            continue

        if "<mods:mods" not in xml:
            print("❌ No MODS record found")
            continue

        print("✅ MODS record retrieved (preview)\n")
        print(xml[:3000])
        time.sleep(SLEEP)


if __name__ == "__main__":
    main()
