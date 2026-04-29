import requests
from bs4 import BeautifulSoup

url = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp?page=3&GroupID=13455"

response = requests.get(url, timeout=20)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "lxml")

print("Статус:", response.status_code)
print("Заголовок:", soup.title.text)
print("=" * 100)

rows = soup.find_all("tr")

for row_num, row in enumerate(rows, start=1):
    cells = row.find_all(["td", "th"])

    row_data = []
    for cell in cells:
        text = cell.get_text(" ", strip=True)
        if text:
            row_data.append(text)

    if row_data:
        print(f"\nСТРОКА {row_num}")
        for item in row_data:
            print(item)
        print("-" * 100)
