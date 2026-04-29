import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://www.do.ektu.kz/PReports/Schedule/ScheduleGroup.asp"


def get_html(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=20)
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "html.parser")


def get_schools_and_years():
    soup = get_html(BASE_URL)
    rows = soup.find_all("tr")

    result = []

    for row in rows:
        cells = row.find_all("td")

        # Нужны строки вида:
        # школа | 2022 | 2023 | 2024 | 2025
        if len(cells) != 5:
            continue

        school_name = cells[0].get_text(" ", strip=True)

        if not school_name:
            continue
        if school_name in ["Школа", "Всего групп:"]:
            continue

        years = ["2022", "2023", "2024", "2025"]

        for i, year in enumerate(years, start=1):
            link = cells[i].find("a")
            count_text = cells[i].get_text(" ", strip=True)

            if link:
                href = link.get("href")
                full_url = urljoin(BASE_URL, href)

                result.append({
                    "school": school_name,
                    "year": year,
                    "count": count_text if count_text else "0",
                    "url": full_url
                })

    return result


def get_groups_by_url(groups_page_url: str):
    soup = get_html(groups_page_url)
    rows = soup.find_all("tr")

    result = []
    current_program_name = ""

    for row in rows:
        cells = row.find_all("td")

        if not cells:
            continue

        # Вариант 1: строка содержит 2 ячейки
        # 1-я = группа, 2-я = образовательная программа
        if len(cells) == 2:
            link = cells[0].find("a")
            if not link:
                continue

            href = link.get("href")
            if not href or "GroupID=" not in href:
                continue

            group_name = cells[0].get_text(" ", strip=True)
            current_program_name = cells[1].get_text(" ", strip=True)

            full_url = urljoin(groups_page_url, href)

            group_id = None
            match = re.search(r"GroupID=(\d+)", full_url)
            if match:
                group_id = match.group(1)

            result.append({
                "group_name": group_name,
                "program_name": current_program_name,
                "group_id": group_id,
                "url": full_url
            })

        # Вариант 2: строка содержит 1 ячейку
        # Это следующая группа той же программы
        elif len(cells) == 1:
            link = cells[0].find("a")
            if not link:
                continue

            href = link.get("href")
            if not href or "GroupID=" not in href:
                continue

            group_name = cells[0].get_text(" ", strip=True)
            full_url = urljoin(groups_page_url, href)

            group_id = None
            match = re.search(r"GroupID=(\d+)", full_url)
            if match:
                group_id = match.group(1)

            result.append({
                "group_name": group_name,
                "program_name": current_program_name,
                "group_id": group_id,
                "url": full_url
            })

    return result


def get_schedule_by_group_id(group_id: str):
    url = f"{BASE_URL}?page=3&GroupID={group_id}"
    soup = get_html(url)

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

        # Строка расписания: 1 ячейка времени + 6 ячеек по дням
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

            # Аудитория
            room_match = re.search(r"\[(.*?)\]", lesson_text)
            if room_match:
                item["room"] = room_match.group(1)

            # Частота
            if "каждая неделя" in lesson_text:
                item["frequency"] = "каждая неделя"

            # Группа / подгруппа
            group_match = re.search(r"\(([^()]*(?:группа|подгруппа)[^()]*)\)\s*$", lesson_text)
            if group_match:
                item["group_info"] = group_match.group(1)

            # Должность преподавателя
            position_match = re.search(r"\((Старший преподаватель|Преподаватель)\)", lesson_text)
            if position_match:
                item["position"] = position_match.group(1)

            # Тип занятия
            for lt in lesson_types:
                pattern = rf"\b{lt}\b"
                if re.search(pattern, lesson_text, re.IGNORECASE):
                    item["lesson_type"] = lt
                    break

            # Преподаватель
            if item["position"]:
                teacher_pattern = rf"каждая неделя\s+(.*?)\s+\({re.escape(item['position'])}\)"
                teacher_match = re.search(teacher_pattern, lesson_text)
                if teacher_match:
                    item["teacher"] = teacher_match.group(1).strip()

            # Предмет
            if item["teacher"] and item["position"] and item["lesson_type"]:
                subject_pattern = rf"\({re.escape(item['position'])}\)\s+(.*?)\s+{re.escape(item['lesson_type'])}"
                subject_match = re.search(subject_pattern, lesson_text)
                if subject_match:
                    item["subject"] = subject_match.group(1).strip()

            schedule.append(item)

    return schedule
