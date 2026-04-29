import requests
from bs4 import BeautifulSoup

url = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp?page=3&GroupID=13455"

response = requests.get(url, timeout=20)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "lxml")

print("Статус:", response.status_code)
print("Заголовок:", soup.title.text)
print("=" * 120)

rows = soup.find_all("tr")

for row_num, row in enumerate(rows, start=1):
    cells = row.find_all(["td", "th"])
    
    if not cells:
        continue

    print(f"\nСТРОКА {row_num} | количество ячеек: {len(cells)}")
    
    for cell_num, cell in enumerate(cells, start=1):
        text = cell.get_text(" ", strip=True)
        print(f"  ЯЧЕЙКА {cell_num}: {repr(text)}")
    
    print("-" * 120)
