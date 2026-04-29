import requests
from bs4 import BeautifulSoup

url = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp?page=3&GroupID=13455"

response = requests.get(url, timeout=20)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "lxml")

days = {
    2: "Понедельник",
    3: "Вторник",
    4: "Среда",
    5: "Четверг",
    6: "Пятница",
    7: "Суббота"
}

schedule = []

rows = soup.find_all("tr")

for row in rows:
    cells = row.find_all(["td", "th"])

    # Нам нужны только строки расписания, где 7 ячеек:
    # 1-я = время, 2-7 = дни недели
    if len(cells) != 7:
        continue

    time_text = cells[0].get_text(" ", strip=True)

    # Пропускаем строки без времени
    if ":" not in time_text:
        continue

    for cell_index in range(1, 7):
        lesson_text = cells[cell_index].get_text(" ", strip=True)

        if lesson_text:
            lesson = {
                "time": time_text,
                "day": days[cell_index + 1],
                "text": lesson_text
            }
            schedule.append(lesson)

print("Найдено занятий:", len(schedule))
print("=" * 100)

for item in schedule:
    print(f"День: {item['day']}")
    print(f"Время: {item['time']}")
    print(f"Текст: {item['text']}")
    print("-" * 100)
