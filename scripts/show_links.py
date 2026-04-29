import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp"

response = requests.get(url, timeout=20)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "html.parser")

print("Статус:", response.status_code)
print("Заголовок:", soup.title.text)
print("=" * 80)

links = soup.find_all("a")

for i, a in enumerate(links, start=1):
    text = a.get_text(" ", strip=True)
    href = a.get("href")

    if href:
        full_href = urljoin(url, href)
    else:
        full_href = None

    print(f"{i}. TEXT: {text}")
    print(f"   HREF: {href}")
    print(f"   FULL: {full_href}")
    print("-" * 80)
