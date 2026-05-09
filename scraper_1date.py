import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

url = "https://www.beatlottery.co.uk/eurojackpot/results/draw_date/2025-09-26"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# --- DRAW DATE and JACKPOT ---
raw_text = soup.get_text(separator="\n")
draw_date = re.search(r"Draw date:?\s*(.+?)(?:\n|$)", raw_text)
draw_date = draw_date.group(1).strip() if draw_date else ""
jackpot = re.search(r"The Jackpot was:?\s*([€0-9,]+)", raw_text)
jackpot = jackpot.group(1).strip() if jackpot else ""

# --- MAIN and EURO NUMBERS (always 5 main + 2 euro by position) ---
ball_tags = soup.find_all('span', class_=re.compile(r"ball"))
numbers = []
for tag in ball_tags:
    num = tag.get_text(strip=True)
    if num.isdigit():
        numbers.append(num.zfill(2))
main_numbers = numbers[:5] if len(numbers) >= 5 else []
euro_numbers = numbers[5:7] if len(numbers) >= 7 else []

print("Main numbers:", main_numbers)
print("Euro numbers:", euro_numbers)

# --- PRIZE BREAKDOWN TABLE ---
table = soup.find("table")
headers = []
header_row = table.find("tr")
if header_row:
    headers = [th.text.strip() for th in header_row.find_all("th")]

rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.text.strip().replace('\u20ac','€') for td in tr.find_all("td")]
    if len(cells) == len(headers) and "Totals" not in cells:
        row = [draw_date, jackpot, " ".join(main_numbers), " ".join(euro_numbers)] + cells
        rows.append(row)

columns = ["draw_date", "jackpot", "main_numbers", "euro_numbers"] + headers
df = pd.DataFrame(rows, columns=columns)
df.to_csv("eurojackpot_full_2025-09-26.csv", index=False, encoding="utf-8")

print("CSV file saved: eurojackpot_full_2025-09-26.csv")
# tämä on toimiva nyt yhden päivän tuloksien kaappaamiseen !!!