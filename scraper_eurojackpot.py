import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import os
from datetime import date, timedelta

# Create 'data' folder if it doesn't exist
os.makedirs('data', exist_ok=True)

def scrape_eurojackpot_date(draw_date_obj):
    draw_date_str = draw_date_obj.strftime("%Y-%m-%d")
    url = f"https://www.beatlottery.co.uk/eurojackpot/results/draw_date/{draw_date_str}"
    print("Scraping", url)
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch", url)
        return [], []
    soup = BeautifulSoup(response.content, "html.parser")
    raw_text = soup.get_text(separator="\n")
    
    draw_date = re.search(r"Draw date:?\s*(.+?)(?:\n|$)", raw_text)
    draw_date = draw_date.group(1).strip() if draw_date else draw_date_str
    jackpot = re.search(r"The Jackpot was:?\s*([€0-9,]+)", raw_text)
    jackpot = jackpot.group(1).strip() if jackpot else ""

    # Extract all ball numbers in order (first 5 main, next 2 euro)
    ball_tags = soup.find_all('span', class_=re.compile(r"ball"))
    numbers = []
    for tag in ball_tags:
        num = tag.get_text(strip=True)
        if num.isdigit():
            numbers.append(num.zfill(2))
    main_numbers = numbers[:5] if len(numbers) >= 5 else []
    euro_numbers = numbers[5:7] if len(numbers) >= 7 else []

    # Weekday string for the draw
    weekday_str = draw_date_obj.strftime("%A")

    # Convert to format dd.mm.yyyy
    date_short = draw_date_obj.strftime("%d.%m.%Y")

    # Table and headers
    table = soup.find("table")
    if not table:
        print("No results table found for", draw_date_str)
        return [], []
    header_row = table.find("tr")
    headers = [th.text.strip() for th in header_row.find_all("th")] if header_row else []

    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.text.strip().replace('\u20ac','€') for td in tr.find_all("td")]
        if len(cells) == len(headers) and "Totals" not in cells:
            # Add new columns for formatted date and weekday
            row = [date_short, weekday_str, draw_date, jackpot, " ".join(main_numbers), " ".join(euro_numbers)] + cells
            rows.append(row)
    return rows, headers

def generate_draw_dates(year):
    # Cutoff for Tuesday draws is 2022-03-25
    tuesday_enabled = False
    tuesday_start = date(2022, 3, 25)
    d = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)
    dates = []
    while d <= end_date:
        if d.weekday() == 4: # Friday always
            dates.append(d)
        if d >= tuesday_start and d.weekday() == 1: # Tuesday after start date
            dates.append(d)
        d += delta
    return sorted(dates)

# Loop for all years and save per year
for yr in range(2012, 2026):
    print(f"\n=== YEAR {yr} ===")
    all_rows = []
    columns = None
    dates = generate_draw_dates(yr)
    for dt in dates:
        rows, headers = scrape_eurojackpot_date(dt)
        if rows:
            if not columns:
                columns = ["short_date", "weekday", "draw_date", "jackpot", "main_numbers", "euro_numbers"] + headers
            all_rows.extend(rows)
    if all_rows and columns:
        fname = os.path.join('data', f"eurojackpot_{yr}_all_draws.csv")
        df = pd.DataFrame(all_rows, columns=columns)
        df.to_csv(fname, index=False, encoding="utf-8")
        print(f"Saved {len(all_rows)} rows to {fname}")
    else:
        print(f"No results found for {yr}")
