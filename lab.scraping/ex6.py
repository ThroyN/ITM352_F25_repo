# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

url = "https://www.hicentral.com/hawaii-mortgage-rates.php"

try:
    r = requests.get(url)  # not adding headers or anything fancy
    html = r.text
except Exception as e:
    print("could not get page:", e)
    raise

soup = BeautifulSoup(html, "html.parser")

# find tables (we'll just guess which one is the rates table)
tables = soup.find_all("table")
if not tables:
    print("no tables found")
    raise SystemExit(1)

target = None
for t in tables:
    ths = t.find_all("th")
    headers = [th.get_text(strip=True).lower() for th in ths]
    # dumb guess: table with lender/bank AND rate/apr in headers
    if any(h in headers for h in ["lender", "bank", "company", "institution"]) and \
       any(("rate" in h) or ("apr" in h) for h in headers):
        target = t
        break

# if we didn't find by headers, just take the first table
if target is None:
    target = tables[0]

rows = target.find_all("tr")
if not rows:
    print("table has no rows")
    raise SystemExit(1)

# try to figure out which column is the bank/lender name
header_row = rows[0].find_all("th")
header_texts = [h.get_text(strip=True).lower() for h in header_row]
lender_idx = 0
for i, h in enumerate(header_texts):
    if h in ["lender", "bank", "company", "institution"]:
        lender_idx = i
        break

# if first row is headers, skip it
start_i = 1 if header_row else 0

print("Mortgage Rates (very basic scrape)")
print("----------------------------------")

for i in range(start_i, len(rows)):
    tds = rows[i].find_all("td")
    if not tds:
        continue

    # lender name
    if lender_idx < len(tds):
        lender = tds[lender_idx].get_text(" ", strip=True)
    else:
        lender = tds[0].get_text(" ", strip=True)

    # collect anything that looks like a rate-ish cell
    rates = []
    for j, td in enumerate(tds):
        if j == lender_idx:
            continue
        txt = td.get_text(" ", strip=True)
        # super simple filter: keep cells with % or "rate" or "apr"
        low = txt.lower()
        if "%" in txt or "apr" in low or "rate" in low:
            rates.append(txt)

    # if we somehow got nothing, just dump the other cells
    if not rates:
        for j, td in enumerate(tds):
            if j != lender_idx:
                cell = td.get_text(" ", strip=True)
                if cell:
                    rates.append(cell)

    if lender:
        print(f"{lender} -> {', '.join(rates)}")
