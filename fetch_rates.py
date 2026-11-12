import json, os, re, sys
import requests

URLS = [
    "https://www.cbsl.gov.lk/cbsl_custom/exratestt/exratestt.php",
    "https://www.cbsl.gov.lk/en/rates-and-indicators/exchange-rates/daily-buy-and-sell-exchange-rates",
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cbsl.gov.lk/en",
}
OUT = "usd_rates.json"

def parse(html):
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text).replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"United\s+States\s+Dollar", text, flags=re.I)
    if not m:
        return {}
    text = text[m.start():]
    rates = {}
    for date, rate in re.findall(r"(\d{4}-\d{2}-\d{2})\s+([\d,]+\.\d+)", text):
        if date in rates:
            break  # next currency's table started
        value = float(rate.replace(",", ""))
        if 150 < value < 600:
            rates[date] = value
    return rates

found = {}
for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(url, "->", r.status_code)
        if r.status_code == 200:
            found = parse(r.text)
            if found:
                break
    except Exception as e:
        print(url, "-> error", e)

if not found:
    print("No rates found. CBSL may be blocking this server.")
    sys.exit(1)

existing = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        existing = json.load(f)
existing.update(found)  # keeps older history, adds/overwrites with fresh data

with open(OUT, "w") as f:
    json.dump(dict(sorted(existing.items())), f, indent=1)
print("Saved", len(existing), "rates. Newest:", max(existing))
