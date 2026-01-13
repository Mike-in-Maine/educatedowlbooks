import requests

ISBN = "9780141439808"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

url = f"https://www.biblio.com/{ISBN}"

r = requests.get(url, headers=HEADERS, timeout=20)

print("STATUS:", r.status_code)
print("FINAL URL:", r.url)
print("HEADERS RETURNED:")
for k, v in r.headers.items():
    print(f"  {k}: {v}")

print("\n--- FIRST 1000 CHARS OF HTML ---\n")
print(r.text[:1000])

# Save full HTML to disk
filename = f"biblio_raw_{ISBN}.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(r.text)

print(f"\nFull HTML saved to {filename}")
