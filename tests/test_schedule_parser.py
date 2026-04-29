from ..src.schedule_parser import get_schools_and_years, get_groups_by_url, get_schedule_by_group_id

# 1. Получаем школы и годы
schools = get_schools_and_years()
print("Всего записей школа+год:", len(schools))
print()

# 2. Ищем Школу цифровых технологий и искусственного интеллекта за 2023
target = None
for item in schools:
    if item["school"] == "Школа цифровых технологий и искусственного интеллекта" and item["year"] == "2023":
        target = item
        break

print("Найдено:")
print(target)
print()

# 3. Получаем группы
groups = get_groups_by_url(target["url"])
print("Групп найдено:", len(groups))
print()

for g in groups[:15]:
    print(g)

print()

# 4. Получаем group_id для 23-ИСК-2
group_id = None
for g in groups:
    if g["group_name"] == "23-ИСК-2":
        group_id = g["group_id"]
        break

print("GroupID для 23-ИСК-2:", group_id)
print()

# 5. Получаем расписание
schedule = get_schedule_by_group_id(group_id)
print("Всего занятий:", len(schedule))
print()

for lesson in schedule[:5]:
    print(lesson)
    print()
