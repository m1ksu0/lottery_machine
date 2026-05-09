import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import date, timedelta

# Existing scraping function, modified to return rows (list of data) for one date
def scrape_eurojackpot_date(draw_date_str):
    url = f"https://www.beatlottery.co.uk/eurojackpot/results/draw_date/{draw_date_str}"
    print("Scraping", url)
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch", url)
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    raw_text = soup.get_text(separator="\n")
    
    draw_date = re.search(r"Draw date:?\s*(.+?)(?:\n|$)", raw_text)
    draw_date = draw_date.group(1).strip() if draw_date else draw_date_str
    jackpot = re.search(r"The Jackpot was:?\s*([€0-9,]+)", raw_text)
    jackpot = jackpot.group(1).strip() if jackpot else ""

    # Extract ball numbers in order (first 5 main, next 2 euro)
    ball_tags = soup.find_all('span', class_=re.compile(r"ball"))
    numbers = []
    for tag in ball_tags:
        num = tag.get_text(strip=True)
        if num.isdigit():
            numbers.append(num.zfill(2))
    main_numbers = numbers[:5] if len(numbers) >= 5 else []
    euro_numbers = numbers[5:7] if len(numbers) >= 7 else []

    # Table and headers
    table = soup.find("table")
    if not table:
        print("No results table found for", draw_date_str)
        return []
    header_row = table.find("tr")
    headers = [th.text.strip() for th in header_row.find_all("th")] if header_row else []

    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.text.strip().replace('\u20ac','€') for td in tr.find_all("td")]
        if len(cells) == len(headers) and "Totals" not in cells:
            row = [draw_date, jackpot, " ".join(main_numbers), " ".join(euro_numbers)] + cells
            rows.append(row)
    return rows, headers

# Generate all Tuesdays & Fridays in 2025 as YYYY-MM-DD strings
def generate_tuesdays_fridays(year=2025):
    d = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)
    dates = []
    while d <= end_date:
        if d.weekday() == 1 or d.weekday() == 4:  # Tuesday=1, Friday=4
            dates.append(d.strftime("%Y-%m-%d"))
        d += delta
    return dates

all_rows = []
columns = None

dates = generate_tuesdays_fridays(2025)
for dt in dates:
    rows, headers = scrape_eurojackpot_date(dt)
    if rows:
        if not columns:
            columns = ["draw_date", "jackpot", "main_numbers", "euro_numbers"] + headers
        all_rows.extend(rows)

# Save combined CSV
if all_rows and columns:
    df = pd.DataFrame(all_rows, columns=columns)
    df.to_csv("eurojackpot_2025_all_tuesdays_fridays.csv", index=False, encoding="utf-8")
    print("Saved all results to eurojackpot_2025_all_tuesdays_fridays.csv")
else:
    print("No results scraped.")
