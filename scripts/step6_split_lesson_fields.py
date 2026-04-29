import requests
from bs4 import BeautifulSoup
import re

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

lesson_types = ["лекция", "лабораторная", "практика", "семинар"]

schedule = []

rows = soup.find_all("tr")

for row in rows:
    cells = row.find_all(["td", "th"])

    if len(cells) != 7:
        continue

    time_text = cells[0].get_text(" ", strip=True)

    if ":" not in time_text:
        continue

    for cell_index in range(1, 7):
        lesson_text = cells[cell_index].get_text(" ", strip=True)

        if not lesson_text:
            continue

        item = {
            "day": days[cell_index + 1],
            "time": time_text,
            "raw_text": lesson_text,
            "room": "",
            "frequency": "",
            "teacher": "",
            "position": "",
            "subject": "",
            "lesson_type": "",
            "group_info": ""
        }

        # 1. Аудитория в квадратных скобках
        room_match = re.search(r"\[(.*?)\]", lesson_text)
        if room_match:
            item["room"] = room_match.group(1)

        # 2. Частота
        if "каждая неделя" in lesson_text:
            item["frequency"] = "каждая неделя"

        # 3. Информация о группе
        group_match = re.search(r"\(([^()]*(?:группа|подгруппа)[^()]*)\)\s*$", lesson_text)
        if group_match:
            item["group_info"] = group_match.group(1)

        # 4. Должность преподавателя
        position_match = re.search(r"\((Старший преподаватель|Преподаватель)\)", lesson_text)
        if position_match:
            item["position"] = position_match.group(1)

        # 5. Тип занятия
        for lt in lesson_types:
            pattern = rf"\b{lt}\b"
            if re.search(pattern, lesson_text, re.IGNORECASE):
                item["lesson_type"] = lt
                break

        # 6. Преподаватель
        if item["position"]:
            teacher_pattern = rf"каждая неделя\s+(.*?)\s+\({re.escape(item['position'])}\)"
            teacher_match = re.search(teacher_pattern, lesson_text)
            if teacher_match:
                item["teacher"] = teacher_match.group(1).strip()

        # 7. Предмет
        if item["teacher"] and item["position"] and item["lesson_type"]:
            subject_pattern = rf"\({re.escape(item['position'])}\)\s+(.*?)\s+{re.escape(item['lesson_type'])}"
            subject_match = re.search(subject_pattern, lesson_text)
            if subject_match:
                item["subject"] = subject_match.group(1).strip()

        schedule.append(item)

print("Найдено занятий:", len(schedule))
print("=" * 120)

for i, lesson in enumerate(schedule[:12], start=1):
    print(f"ЗАНЯТИЕ {i}")
    print("День:", lesson["day"])
    print("Время:", lesson["time"])
    print("Аудитория:", lesson["room"])
    print("Частота:", lesson["frequency"])
    print("Преподаватель:", lesson["teacher"])
    print("Должность:", lesson["position"])
    print("Предмет:", lesson["subject"])
    print("Тип занятия:", lesson["lesson_type"])
    print("Группа:", lesson["group_info"])
    print("RAW:", lesson["raw_text"])
    print("-" * 120)
